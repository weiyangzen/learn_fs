# File Research: sources/os/plan9/plan9/sys/src/cmd/file.c

Plan 9 `file` command implementation for classifying file content and optional MIME type output.

Key behavior:
- Reads up to 6000 bytes, builds character and Unicode script histograms, and classifies gross content as ascii, latin, UTF, extended ascii, null/binary.
- Checks a sequence of recognizers: magic at offset 0, string prefixes, ELF, Plan 9 executable headers, IFF/RIFF, offset magic, offset strings, email/mbox, tar, HTML, compiler intermediates, source code heuristics, Plan 9 fonts/images, RTF, MSDOS executables, ascii face files, entropy-based compressed/encrypted data, and English text.
- Supports `-m` MIME output.
- Handles directories and non-ordinary special files before reading content.

Important implementation details:
- `long0tab`, `longofftab`, `file_string`, and `offstrs` are the primary magic tables.
- `wordfreq()` recognizes language keywords for C/Alef/Fortran/Limbo/assembler heuristics.
- `isp9bit()` parses old and new Plan 9 image headers, including compressed image prefixes and subfont trailers.
- `print_utf()` reports script names for Unicode-heavy text.
- Uses `crackhdr()` from `mach.h` to identify native executable formats.

Risks and invariants:
- Many recognizers are heuristic and order-dependent.
- MIME output is sometimes a coarse fallback such as `application/octet-stream`.
- `ismung()` names low-entropy distribution over high bits as compressed/encrypted based on a small sample.
