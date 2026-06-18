# sources/test-tools/fio/lib/pattern.c

Purpose: parses, copies, compares, and fills fio buffer verification patterns. Inputs can combine quoted strings, quoted file contents, decimal values, hexadecimal byte strings, and placeholder formats such as `%o`.

Important APIs/functions: `parse_and_fill_pattern_alloc`, `cpy_pattern`, `cmp_pattern`, `paste_format_inplace`, and `paste_format`. Internal parsers handle file reads, quoted strings, decimal/hex numbers, and format descriptors.

Control flow: parsing first supports a sizing pass with `out == NULL`, then allocates and performs a fill pass. `cpy_pattern` copies one pattern chunk and duplicates it exponentially across the output. `cmp_pattern` first checks repeated pattern structure inside the buffer, then compares against the expected pattern offset. Paste functions reserve descriptor-sized holes and later invoke descriptor callbacks to write dynamic fields.

State/persistence: file pattern parsing reads external files; allocated pattern buffers are returned to callers. Format arrays are caller-provided and filled with offsets and descriptors.

Dependencies/integration: uses `strntol`, fio `min`, `strcasestr`, `strndup`, file I/O, errno values, and pattern descriptors from `pattern.h`. It integrates with verify buffer generation and dynamic offset insertion.

Risks/test signals: quoted strings cannot escape quotes; file reads can truncate to `out_len`; decimal parsing is limited to `INT_MIN..INT_MAX`; hex parsing has special handling for adjacent `0x`. Tests should cover malformed inputs, maximum pattern size, file patterns, placeholders crossing pattern length, copy/compare offsets, and negative decimal byte order.
