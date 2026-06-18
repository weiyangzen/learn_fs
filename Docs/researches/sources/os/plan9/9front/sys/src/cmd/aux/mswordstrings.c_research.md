# File Research: sources/os/plan9/9front/sys/src/cmd/aux/mswordstrings.c

`mswordstrings` extracts plain-ish text from an OLE-mounted Word `WordDocument` stream. It reads the Word FIB header, seeks from `fcMin` to `fcMac`, and translates control characters into newlines, tabs, field markers, placeholder labels, or suppressed output.

The generated `Fibhdr` reader decodes little-endian fields and bit flags from the first 0x22 bytes. Only the basic text range is used; formatting, piece tables, compression, encryption, and Unicode runs are not fully parsed.

Special mappings include paragraph end to blank line, hard/page breaks to newlines, field begin/separator/end to `<`, `:`, `>`, and some embedded object/date/time placeholders. Zero bytes are skipped to tolerate mixed single-byte and interleaved-zero text regions.
