# sources/sync-backup/rsync/lib/permstring.h

Purpose: declares the permission-string buffer size and formatter API.

Important APIs/types/functions: `PERMSTRING_SIZE` is `11`, and `permstring(char *perms, mode_t mode)` writes a 10-character mode string plus null terminator.

Control flow: no runtime logic.

State and persistence behavior: no state. It encodes the caller buffer-size contract for `permstring.c`.

Dependencies/integration: included through `rsync.h` and direct callers that format file modes.

Risks/test signals: callers that allocate fewer than 11 bytes will overflow. Static analysis or compile-time helper usage should prefer `PERMSTRING_SIZE`.
