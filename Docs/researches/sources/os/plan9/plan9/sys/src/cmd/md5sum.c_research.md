# File Research: sources/os/plan9/plan9/sys/src/cmd/md5sum.c

Implements an MD5 checksum command.

Key functions:
- `digestfmt()` installs `%M` formatting for MD5 byte arrays as lowercase hex.
- `sum()` streams an fd through Plan 9 `md5()`, reports read errors, and prints digest with optional filename.
- `main()` parses no options, installs formatter, and processes stdin or each named file.

Dependencies:
- `<libsec.h>` MD5 APIs.
- Plan 9 `Bio` is included but not materially used.

Output:
- Stdin: `<digest>`.
- Files: `<digest>\t<name>`.
