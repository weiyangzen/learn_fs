# File Research: sources/os/plan9/9front/sys/src/cmd/auth/authcmdlib.h

Shared declarations for Plan 9 auth command support library.

Key contents:
- Sets library pragma for `./lib.$O.a`.
- Defines key database paths, auth log name, max challenge/path constants, account bio structures, filesystem descriptors, and Plan 9/Securenet selector constants.
- Declares helper functions for password/key management, key lookup, challenge checks, account bio read/write, logging, and file I/O.
- Declares `%K` formatting for DES keys.

Role:
- Shared contract for auth commands such as `authsrv`, `changeuser`, and bio conversion tools.

Research notes:
- The header exposes legacy DES/Securenet and newer AES/auth key helpers side by side.
