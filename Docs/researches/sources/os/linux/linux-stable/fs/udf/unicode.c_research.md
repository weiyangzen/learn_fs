# File Research: sources/os/linux/linux-stable/fs/udf/unicode.c

## Summary
Converts between OSTA Compressed Unicode CS0 filenames/dstrings and Linux UTF-8 or configured NLS charset names, including UDF filename mangling with CRC suffixes.

## Main Responsibilities
- Decodes CS0 8-bit or 16-bit compressed Unicode.
- Handles UTF-16 surrogate pairs and rejects malformed Unicode.
- Converts decoded Unicode through NLS `uni2char` or UTF-8.
- Replaces illegal or unconvertible characters and adds CRC markers when needed.
- Preserves short filename extensions where possible during mangling.
- Encodes Linux names back into CS0, using 8-bit compression when possible and 16-bit/UTF-16 surrogate pairs when needed.
- Converts informational UDF dstrings with tolerant truncation.

## Important Behavior
`udf_get_filename()` uses translation mode, so names containing `/`, empty names, dot/dotdot ambiguities, invalid Unicode, or overlong output may be rewritten with `_` and `#XXXX` CRC fragments.

`udf_put_filename()` returns zero when a name cannot fit into the target CS0 buffer.

## Risks
Filename conversion affects lookup, creation, symlink serialization, and volume labels. CRC mangling is essential to preserve distinguishability after invalid-character replacement or truncation.
