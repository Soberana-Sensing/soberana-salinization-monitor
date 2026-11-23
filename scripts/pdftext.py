#!/usr/bin/env python3
"""Extract text from PDF files with no external dependencies.

This box has no pip, no pdftotext, no mutool, no qpdf, no ghostscript and no Java.
This script parses the PDF itself: FlateDecode content streams, ToUnicode CMaps, and
the Tj / TJ text-showing operators.

It exists because papers have to be read as text, not as PDF uploads. Vendored here on
2026-10-07 after the /tmp copy was lost.

Usage:
    python3 pdftext.py FILE.pdf                 # to stdout
    python3 pdftext.py --out-dir DIR FILE.pdf   # to DIR/<paper-name>.txt
    python3 pdftext.py --out-dir DIR *.pdf      # batch

Two engines. The built-in parser needs nothing but the standard library. PyMuPDF (pip install
pymupdf) is used when it is importable, because it decodes CID-keyed Type1 fonts that the built-in
parser cannot touch. Run the script with the project venv to get the better engine:

    ~/soberana-sensing/soberana-soil/soberana-soil-venv/bin/python pdftext.py paper.pdf

Force an engine with --engine builtin or --engine pymupdf. PyMuPDF output is cleaner prose and
recovers tables, so prefer it when it is available.

Three bugs cost real time when this was first written. They are handled below and each
is marked BUG. Do not "simplify" them away:

  BUG 1  Single-byte Type1 fonts must be decoded one byte at a time. Treating them as
         2-byte Identity-H silently yields empty strings, because their ToUnicode keys
         are below 0x100 and never match a 2-byte key.
  BUG 2  Byte width must come from the font /Subtype, never from a heuristic such as
         "cmap longer than 200 entries". A 248-entry Type1 cmap broke that heuristic.
  BUG 3  Some PDFs put the font resource dict inline on the page (/Font 325 0 R rather
         than /Resources N 0 R). Miss that and every glyph falls through to a latin-1
         decode of two-byte codes, which looks like a scanned document but is not one.
"""

import argparse
import re
import sys
import zlib
from pathlib import Path

# ---------------------------------------------------------------- PDF primitives

OBJ_RE = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj", re.S)
STREAM_RE = re.compile(rb"stream\r?\n(.*?)\r?\n?endstream", re.S)
DICT_REF_RE = re.compile(rb"(\d+)\s+(\d+)\s+R")


def load_objects(data):
    """Map object number -> raw body bytes."""
    objects = {}
    for match in OBJ_RE.finditer(data):
        objects[int(match.group(1))] = match.group(3)
    return objects


def get_stream(body):
    """Return the decoded stream payload of an object body, or None."""
    match = STREAM_RE.search(body)
    if not match:
        return None
    raw = match.group(1)
    head = body[: match.start()]
    if b"FlateDecode" in head:
        try:
            return zlib.decompress(raw)
        except zlib.error:
            try:
                # Truncated or slightly corrupt stream: salvage what we can.
                return zlib.decompressobj().decompress(raw)
            except zlib.error:
                return None
    if b"Filter" in head:
        return None  # LZW, DCT, JPX, CCITT: not worth supporting here
    return raw


def resolve(objects, value):
    """Follow an indirect reference if value is one, else return value unchanged."""
    if not isinstance(value, bytes):
        return value
    match = DICT_REF_RE.fullmatch(value.strip())
    if match and int(match.group(1)) in objects:
        return objects[int(match.group(1))]
    return value


# ------------------------------------------------------------------- ToUnicode

def parse_cmap(stream):
    """Parse a ToUnicode CMap into {code: text}. Handles 1-byte and 2-byte codes."""
    cmap = {}
    if not stream:
        return cmap

    # bfchar sections: <src> <dst>
    for section in re.findall(rb"beginbfchar(.*?)endbfchar", stream, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]*)>", section):
            code = int(src, 16)
            cmap[code] = hex_to_text(dst)
            # BUG 1: expose the 1-byte key as well, so single-byte decoders find it.
            if code < 0x100:
                cmap.setdefault(code, cmap[code])

    # bfrange sections, the <lo> <hi> <dst> form
    for section in re.findall(rb"beginbfrange(.*?)endbfrange", stream, re.S):
        pattern = re.compile(
            rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>"
            rb"|"
            rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*?)\]",
            re.S,
        )
        for block in re.findall(rb"\[(.*?)\]", section, re.S):
            pass  # array form handled below via the flat regex
        for match in pattern.finditer(section):
            lo_s, hi_s, dst_s, lo_a, hi_a, arr = match.groups()
            if arr:
                items = re.findall(rb"<([0-9A-Fa-f]*)>", arr)
                start = int(lo_a, 16)
                for offset, item in enumerate(items):
                    cmap[start + offset] = hex_to_text(item)
                continue
            lo, hi = int(lo_s, 16), int(hi_s, 16)
            base = int(dst_s, 16)
            width = len(dst_s)
            # A bfrange can span a huge range on damaged files. Cap it rather than
            # building a dictionary of millions of entries.
            span = min(hi - lo + 1, 65536)
            for offset in range(span):
                code = lo + offset
                shifted = base + offset
                if width <= 2:
                    text = hex_to_text("%0*X" % (width, shifted))
                else:
                    try:
                        text = chr(shifted).encode("utf-16-be", "surrogatepass").decode(
                            "utf-16-be", "ignore"
                        )
                    except (OverflowError, ValueError):
                        text = ""
                cmap[code] = text
                if code < 0x100:
                    cmap.setdefault(code, text)
    return cmap


GLYPH_NAMES = {b"space": " ", b"hyphen": "-", b"period": ".", b"comma": ","}


def glyph_to_char(name):
    """Resolve a simple PDF glyph name to a character."""
    if name in GLYPH_NAMES:
        return GLYPH_NAMES[name]
    if len(name) == 1:
        return name.decode("latin-1")
    return ""


def hex_to_text(value):
    """Turn a <hex> destination string into text, honouring 2-byte UTF-16BE pairs."""
    if not value:
        return ""
    try:
        raw = bytes.fromhex(value.decode("ascii"))
    except (ValueError, UnicodeDecodeError):
        return ""
    if len(raw) % 2 == 0 and len(raw) >= 2:
        return raw.decode("utf-16-be", "ignore")
    return raw.decode("latin-1", "ignore")


# ----------------------------------------------------------------- font loading

FONT_KEYS = (b"/Type0", b"/TrueType", b"/Type1", b"/Type3", b"/CIDFontType0", b"/CIDFontType2")


def build_font_map(objects, page_resources):
    """Return {font object number: (cmap, is_two_byte)}.

    BUG 2: byte width comes from /Subtype only. /Type0 means two-byte Identity-H or
    Identity-V; everything else is one byte.
    """
    fonts = {}
    if not page_resources:
        return fonts

    font_blob = None
    position = page_resources.find(b"/Font")
    if position != -1:
        tail = page_resources[position + 5 :]
        # Either an indirect reference to a font dict, or an inline dictionary.
        indirect = re.match(rb"\s*(\d+)\s+\d+\s+R", tail)
        if indirect:
            font_blob = objects.get(int(indirect.group(1)), b"")
        else:
            inline = re.match(rb"\s*<<", tail)
            if inline:
                depth = 0
                end = inline.end()
                for offset in range(inline.end() - 2, len(tail)):
                    if tail[offset : offset + 2] == b"<<":
                        depth += 1
                    elif tail[offset : offset + 2] == b">>":
                        depth -= 1
                        if depth == 0:
                            end = offset
                            break
                font_blob = tail[: end + 2]
    if font_blob is None:
        return fonts

    for name, num_s, gen_s in re.findall(
        rb"/([A-Za-z0-9#+.\-]+)\s+(\d+)\s+(\d+)\s+R", font_blob
    ):
        number = int(num_s)
        body = objects.get(number)
        if body is None:
            continue

        subtype = None
        head = body.split(b"stream", 1)[0]
        subtype_match = re.search(rb"/Subtype\s*/([A-Za-z0-9]+)", head)
        if subtype_match:
            subtype = subtype_match.group(1)
        is_two_byte = subtype == b"Type0"

        # A Type0 font's descendant may carry the real width; inherit otherwise.
        if subtype == b"Type0":
            desc_match = re.search(rb"/DescendantFonts\s*\[\s*(\d+)\s+\d+\s+R", body)
            if desc_match:
                descendant = objects.get(int(desc_match.group(1)), b"")
                if b"/CIDFontType2" in descendant:
                    is_two_byte = True

        # ToUnicode CMap, reached through the font descriptor or directly.
        cmap = {}
        tu_match = re.search(rb"/ToUnicode\s+(\d+)\s+\d+\s+R", body)
        if tu_match:
            cmap_body = objects.get(int(tu_match.group(1)))
            if cmap_body:
                stream = get_stream(cmap_body)
                cmap = parse_cmap(stream)

        if not cmap:
            # Follow the descriptor's /ToUnicode when the font points at one indirectly.
            desc = re.search(rb"/FontDescriptor\s+(\d+)\s+\d+\s+R", body)
            if desc:
                desc_body = objects.get(int(desc.group(1)), b"")
                tu2 = re.search(rb"/ToUnicode\s+(\d+)\s+\d+\s+R", desc_body)
                if tu2:
                    cmap = parse_cmap(get_stream(objects.get(int(tu2.group(1)), b"")))

        # Last resort: a CMap stream whose resource name matches this font's base name.
        # BUG 5: do NOT scan every object for any CMap. Doing so hands a font the table
        # belonging to some other font, which decodes into confident-looking garbage.
        # Matching on the base name is the only safe version of this fallback.

        # No ToUnicode: fall back to the declared encoding. WinAnsiEncoding is cp1252,
        # which is close enough to latin-1 for the ASCII range that carries the prose.
        # /Differences, when present, override individual codes via the glyph names.
        if not cmap:
            cmap = {}
            head_text = head
            diff = re.search(rb"/Differences\s*\[(.*?)\]", head_text, re.S)
            if diff:
                for code, glyph in re.findall(
                    rb"(\d+)\s*/([A-Za-z0-9#]+)", diff.group(1)
                ):
                    cmap[int(code)] = glyph_to_char(glyph)
            encoding = b"WinAnsiEncoding" if b"/WinAnsiEncoding" in head_text else b"MacRomanEncoding"
            for code in range(32, 256):
                cmap.setdefault(code, bytes([code]).decode("cp1252", "replace"))

        fonts[b"/" + name] = (cmap, is_two_byte)
    return fonts


# ------------------------------------------------------------- text extraction

def decode_string(raw, cmap, is_two_byte):
    """Decode a PDF literal string using a font's CMap."""
    out = []
    if is_two_byte:
        for i in range(0, len(raw) - 1, 2):
            code = (raw[i] << 8) | raw[i + 1]
            out.append(cmap.get(code, ""))
    else:
        for byte in raw:
            out.append(cmap.get(byte, chr(byte)))
    return "".join(out)


def unescape(raw):
    """Resolve PDF literal-string escapes."""
    out = bytearray()
    i = 0
    simple = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12}
    while i < len(raw):
        char = raw[i]
        if char != 0x5C:  # backslash
            out.append(char)
            i += 1
            continue
        i += 1
        if i >= len(raw):
            break
        nxt = raw[i]
        if nxt in simple:
            out.append(simple[nxt])
            i += 1
        elif 0x30 <= nxt <= 0x37:  # octal
            digits = ""
            while i < len(raw) and len(digits) < 3 and 0x30 <= raw[i] <= 0x37:
                digits += chr(raw[i])
                i += 1
            out.append(int(digits, 8) & 0xFF)
        elif nxt in (10, 13):  # line continuation
            i += 1
            if nxt == 13 and i < len(raw) and raw[i] == 10:
                i += 1
        else:
            out.append(nxt)
            i += 1
    return bytes(out)


def split_strings(blob):
    """Return the literal and hex string operands inside a TJ array body."""
    out = []
    i = 0
    length = len(blob)
    while i < length:
        char = blob[i : i + 1]
        if char == b"(":
            i += 1
            buf = bytearray()
            depth = 1
            while i < length:
                c = blob[i : i + 1]
                if c == b"\\":
                    buf += blob[i : i + 2]
                    i += 2
                    continue
                if c == b"(":
                    depth += 1
                elif c == b")":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                buf += c
                i += 1
            out.append(b"(" + bytes(buf) + b")")
        elif char == b"<" and blob[i + 1 : i + 2] != b"<":
            end = blob.find(b">", i)
            if end == -1:
                break
            out.append(blob[i : end + 1])
            i = end + 1
        else:
            i += 1
    return out


STRING_RE = re.compile(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>", re.S)
ARRAY_OPEN = b"["
ARRAY_CLOSE = b"]"


OPERATOR_CHARS = b"/[]()<>{}%"


def tokenize(stream):
    """Yield (kind, value) tokens: 'string', 'hex', 'array', 'name', 'number', 'op'.

    A real tokenizer, not a scan for the operators we happen to care about. Operand
    and operator boundaries have to be right or fonts bind to the wrong strings.
    """
    i = 0
    length = len(stream)
    while i < length:
        char = stream[i : i + 1]

        if char in b" \t\r\n\f\x00":
            i += 1
            continue

        if char == b"%":  # comment to end of line
            end = stream.find(b"\n", i)
            i = length if end == -1 else end + 1
            continue

        if char == b"(":  # literal string
            i += 1
            buf = bytearray()
            depth = 1
            while i < length:
                c = stream[i : i + 1]
                if c == b"\\":
                    buf += stream[i : i + 2]
                    i += 2
                    continue
                if c == b"(":
                    depth += 1
                elif c == b")":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                buf += c
                i += 1
            yield "string", bytes(buf)
            continue

        if char == b"<":
            if stream[i + 1 : i + 2] == b"<":
                depth = 0
                while i < length:
                    if stream[i : i + 2] == b"<<":
                        depth += 1
                        i += 2
                    elif stream[i : i + 2] == b">>":
                        depth -= 1
                        i += 2
                        if depth == 0:
                            break
                    else:
                        i += 1
                yield "dict", None
                continue
            end = stream.find(b">", i)
            if end == -1:
                break
            yield "hex", re.sub(rb"[^0-9A-Fa-f]", b"", stream[i + 1 : end])
            i = end + 1
            continue

        if char == b">" and stream[i + 1 : i + 2] == b">":
            i += 2
            continue

        if char == b"[":  # array: flatten, the items inside are the operands
            i += 1
            depth = 1
            while i < length and depth:
                c = stream[i : i + 1]
                if c == b"\\":
                    i += 2
                    continue
                if c == b"<" and stream[i + 1 : i + 2] != b"<":
                    end = stream.find(b">", i)
                    if end == -1:
                        break
                    yield "hex", re.sub(rb"[^0-9A-Fa-f]", b"", stream[i + 1 : end])
                    i = end + 1
                    continue
                if c == b"(":
                    i += 1
                    buf = bytearray()
                    inner = 1
                    while i < length:
                        cc = stream[i : i + 1]
                        if cc == b"\\":
                            buf += stream[i : i + 2]
                            i += 2
                            continue
                        if cc == b"(":
                            inner += 1
                        elif cc == b")":
                            inner -= 1
                            if inner == 0:
                                i += 1
                                break
                        buf += cc
                        i += 1
                    yield "string", bytes(buf)
                    continue
                if c == b"[":
                    depth += 1
                elif c == b"]":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
            continue

        if char in b"]})>":
            i += 1
            continue

        if char == b"/":
            match = re.match(rb"/([^\s/\[\]<>(){}%]*)", stream[i:])
            yield "name", match.group(1)
            i += match.end()
            continue

        match = re.match(rb"[+-]?(\d+\.?\d*|\.\d+)", stream[i:])
        if match:
            yield "number", match.group(0)
            i += match.end()
            continue

        match = re.match(rb"[A-Za-z*'\"01]+", stream[i:])
        if match:
            yield "op", match.group(0)
            i += match.end()
            continue

        i += 1


def extract_page(stream, fonts, depth=0):
    """Pull text-showing operators out of one content stream."""
    out = []
    current = ({}, False)
    font_name = None
    operands = []
    last_y = None

    for kind, value in tokenize(stream):
        if kind == "name":
            font_name = value
            continue
        if kind == "string":
            operands.append(("string", value))
            continue
        if kind == "hex":
            operands.append(("hex", value))
            continue
        if kind == "number":
            operands.append(("number", value))
            continue
        if kind != "op":
            continue

        operator = value

        if operator == b"Tf":
            current = fonts.get(b"/" + (font_name or b""), ({}, False))
        elif operator in (b"Tj", b"TJ", b"'", b'"'):
            # BUG 6: decode with the font that was current for THESE operands, not
            # whatever font happens to be current when the operator is reached.
            cmap, is_two_byte = current
            for operand_kind, operand in operands:
                if operand_kind == "number":
                    # TJ kerning. A negative adjustment wider than a space means the
                    # writer put a real gap there; below that it is letter fit.
                    if operator == b"TJ":
                        try:
                            if float(operand) <= -170:
                                out.append(" ")
                        except (TypeError, ValueError):
                            pass
                    continue
                if operand_kind == "string":
                    out.append(decode_string(unescape(operand), cmap, is_two_byte))
                else:
                    raw = operand
                    if len(raw) % 2:
                        raw += b"0"
                    try:
                        out.append(
                            decode_string(bytes.fromhex(raw.decode()), cmap, is_two_byte)
                        )
                    except ValueError:
                        pass
        elif operator == b"T*":
            out.append("\n")
        elif operator in (b"TD", b"ET"):
            # TD carries the dy as an operand, handled with Td below. ET alone is not
            # a line break: most writers wrap every glyph run in its own BT/ET, so
            # breaking on ET splits words at every run boundary ("Goal" + "s").
            pass
        elif operator == b"Tm":
            # BUG 7: Td/Tm repositioning is also how kerning and word spacing are
            # expressed. Breaking on every move shreds words ("U nive rsiti", "Goal s").
            # Break only on a genuine vertical move to a new line of type.
            numbers = [
                v for k, v in operands if k == "number"
            ]
            if len(numbers) >= 6 and last_y is not None:
                try:
                    y = float(numbers[5])
                    if last_y is not None and y < last_y - 3.0:
                        out.append("\n")
                    last_y = y
                except (TypeError, ValueError):
                    pass
            elif len(numbers) >= 6:
                try:
                    last_y = float(numbers[5])
                except (TypeError, ValueError):
                    pass
        elif operator == b"Td":
            # Same rule: only a real downward step ends the line.
            numbers = [v for k, v in operands if k == "number"]
            if numbers:
                try:
                    if float(numbers[-1]) < -1.0:
                        out.append("\n")
                except (TypeError, ValueError):
                    pass

        operands = []

    return "".join(out)


def normalize(text):
    """Collapse PDF spacing into readable prose.

    PDF positions each glyph run separately, so correct text still arrives shredded into
    one-line fragments ("U" / "nive" / "rsiti"). Rejoin those, but keep real breaks:
    a line ends only when the next line starts a new sentence, capitalises mid-line
    continuation, or the fragment looks like it ends a paragraph.
    """
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]

    out = []
    for line in lines:
        if out and _continues(out[-1], line):
            out[-1] = _join(out[-1], line)
        else:
            out.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def _join(previous, line):
    """Concatenate two fragments, restoring the space the PDF positioning removed."""
    if not previous or not line:
        return previous + line
    # No space before punctuation or after an opening bracket.
    if line[0] in ".,;:!?)%]/" or previous[-1] in "([{/":
        return previous + line
    return previous + " " + line


def _continues(previous, line):
    """True when `line` is a continuation fragment rather than a new line of text."""
    if not previous:
        return False
    if previous.endswith((".", "!", "?", ":", ";")):
        return False
    # A sentence break followed by a capital is a new line.
    if re.search(r"[a-z0-9)\]]\s+[A-Z]$", previous) and re.match(r"[A-Z]", line):
        return False
    # Reference headers: "Vol." style endings.
    if re.search(r"\b(et al|ibid|vol|pp|no|eds?)\.$", previous, re.I):
        return False
    # Short fragments are continuations of a word or phrase.
    if len(previous) < 90 or len(line) < 90:
        return True
    return False


def extract_pymupdf(path):
    """Return the extracted text of a PDF file using PyMuPDF, or None if unavailable."""
    try:
        import pymupdf
    except ImportError:
        return None
    with pymupdf.open(path) as document:
        pages = [page.get_text() for page in document]
    return "\n\n".join(pages).strip()


def extract(path, engine="auto"):
    """Return the extracted text of a PDF file.

    engine: "auto" uses PyMuPDF when importable, else the built-in parser; "builtin" and
    "pymupdf" force one. The built-in parser is the one with the three BUGs below.
    """
    if engine in ("auto", "pymupdf"):
        text = extract_pymupdf(path)
        if text:
            return text
        if engine == "pymupdf":
            return ""
    return extract_builtin(path)


def extract_builtin(path):
    """Return the extracted text of a PDF file, built-in parser only."""
    data = Path(path).read_bytes()
    objects = load_objects(data)

    pages = []
    for number, body in sorted(objects.items()):
        head = body.split(b"stream", 1)[0]
        if re.search(rb"/Type\s*/Page\b", head) and b"/Pages" not in head:
            pages.append((number, body))

    if not pages:
        # Some writers keep no explicit /Page objects. Fall back to every content stream.
        return normalize(
            "\n\n".join(
                filter(
                    None,
                    (
                        normalize(extract_page(s, {}))
                        for s in (get_stream(b) for b in objects.values())
                        if s and b"Tj" in s or (s and b"TJ" in s)
                    ),
                )
            )
        )

    texts = []
    for _, body in pages:
        resources = b""

        # BUG 3: the font dict can be inline on the page rather than behind /Resources.
        inline = re.search(rb"/Font\s*(\d+)\s+\d+\s+R", body)
        if inline and int(inline.group(1)) in objects:
            resources = objects[int(inline.group(1))]
        else:
            res_match = re.search(rb"/Resources\s*(\d+)\s+\d+\s+R", body)
            if res_match and int(res_match.group(1)) in objects:
                resources = objects[int(res_match.group(1))]
            else:
                res_match = re.search(rb"/Resources\s*(<<.*)", body, re.S)
                if res_match:
                    resources = res_match.group(1)

        fonts = build_font_map(objects, resources)

        streams = []
        # Try the array form first. "/Contents\r[ 305 0 R ...]" is common, and a
        # regex expecting a digit straight after /Contents silently misses it.
        array = re.search(rb"/Contents\s*\[(.*?)\]", body, re.S)
        if array:
            for num_s, _gen_s in re.findall(rb"(\d+)\s+(\d+)\s+R", array.group(1)):
                streams.append(get_stream(objects.get(int(num_s), b"")))
        else:
            contents = re.search(rb"/Contents\s*(\d+)\s+\d+\s+R", body, re.S)
            if contents:
                streams.append(get_stream(objects.get(int(contents.group(1)), b"")))

        for stream in streams:
            if stream:
                texts.append(extract_page(stream, fonts))

    return normalize("\n\n".join(texts))


# ------------------------------------------------------------------------ main

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="+")
    parser.add_argument("--out-dir", help="write one .txt per PDF here")
    parser.add_argument(
        "--engine",
        choices=("auto", "builtin", "pymupdf"),
        default="auto",
        help="auto uses PyMuPDF when importable, else the built-in parser",
    )
    args = parser.parse_args()

    for pdf in args.pdfs:
        text = extract(pdf, args.engine)
        if args.out_dir:
            out = Path(args.out_dir) / (Path(pdf).stem + ".txt")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            print(f"{out}  {len(text)} chars")
        else:
            print(text)


if __name__ == "__main__":
    sys.exit(main())