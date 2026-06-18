# File Research: sources/local-fs/xfsprogs/db/strvec.h

Header for NULL-terminated string vector utilities.

Key responsibilities:
- Declares allocation, append, copy, free, and print helpers.

Dependencies:
- Used by command parsing or output code needing string-vector ownership helpers.

Notable risks:
- API does not encode vector length, so callers must maintain NULL termination.
