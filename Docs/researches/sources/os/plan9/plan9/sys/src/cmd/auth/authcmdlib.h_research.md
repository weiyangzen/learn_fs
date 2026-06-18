# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/authcmdlib.h

Shared declarations for Plan 9 auth command utilities.

Key points:
- Defines constants for key database paths, password length, SecureNet challenge limits, and account bio fields.
- Defines `Acctbio` and `Fs` structs.
- Declares helpers for key lookup, secret lookup/update, password input/validation, net response checking, account bio parsing/writing, file IO, logging, and formatting.

Dependencies:
- Used by many files in `cmd/auth`.

Notable behavior:
- Declares `#pragma lib "./lib.$O.a"` to link local auth command library.
