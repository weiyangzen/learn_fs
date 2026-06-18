# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.c

Read completely: 259 lines.

This module implements an ISO-646 variant mapper for a fixed set of special ASCII code points: `#`, `$`, `@`, brackets, backslash, caret, grave, braces, vertical bar, and tilde. A description file supplies replacement values for those positions.

Key behavior: the variable string optionally starts with `!` to request backward mapping, followed by a file path relative to the mapper directory. `parse_file` memory-maps that file and reads one numeric mapping per special code. Forward conversion maps special ASCII through the table, passes other ASCII through, rejects `src >= 0x80`, and treats `INVALID` table entries as non-identical. Backward conversion reverses table entries, rejects ambiguous source special bytes, and treats non-ASCII as non-identical.

Important interactions: uses mapper ABI, memstream, mmap, and BCS helpers.

Security/reliability notes: path construction uses `PATH_MAX` and `snprintf`, but truncation is not explicitly detected. In `parse_file`, after `strtoul`, the code calls `_bcs_skip_ws(buf)` rather than skipping from the parse end pointer, which appears to make the trailing-content validation ineffective or inverted for normal numeric lines; this parser deserves targeted tests before format changes.
