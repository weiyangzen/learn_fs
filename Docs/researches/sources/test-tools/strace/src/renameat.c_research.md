# sources/test-tools/strace/src/renameat.c

Purpose: Decodes `renameat` and `renameat2` syscall arguments.

Important APIs/types/functions: syscall decoder functions for rename-at variants and flag xlat handling for `renameat2`.

Control flow: prints old directory fd/path and new directory fd/path; `renameat2` additionally prints flags symbolically. Returns decoded on entry because outputs are not produced.

State and persistence: stateless.

Dependencies/integration: fd/path printers and rename flag xlat tables.

Risks: `AT_FDCWD` and path pointer failures must render consistently with other *at syscalls. Unknown flags should be preserved.

Test signals: renameat/renameat2 with `AT_FDCWD`, relative paths, invalid paths, `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, unknown flags, and xlat modes.
