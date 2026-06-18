# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/error.h

Vac error string declaration header.

Behavior:
- Undefines `EIO` first, because host headers such as macOS `<errno.h>` may define it as a macro.
- Declares all error strings defined in `error.c`, including directory, metadata, block, path, read-only, removed, existence, and root-removal errors.

This keeps Vac’s symbolic error names portable across host build environments.
