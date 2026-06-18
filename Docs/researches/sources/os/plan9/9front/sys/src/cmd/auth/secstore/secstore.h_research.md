# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/secstore.h

Shared secstore declarations and constants. Defines:
- `LOG` as `"secstore"`.
- `SECSTORE_DIR` as `/adm/secstore`.
- `MAXFILESIZE` as 10 MiB.
- password/account status bits: `Enabled` and `STA`.

Core data structure:
- `PW` holds secstore account metadata: user id, expiry, status bits, failed-login count, comments/other info, and the PAK verifier `Hi`.

Declared interfaces:
- Password file lifecycle: `freePW`, `getPW`, `putPW`.
- Server filename filter: `validatefile`.
- PAK functions: `PAKclient`, `PAKserver`, `PAK_Hi`.

Filesystem relevance:
- Establishes `/adm/secstore` as the backing administration tree and constrains secstore per-file sizes.
