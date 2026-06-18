# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomwrite.c

Server write and truncate handlers.

Key functions:
- `smbtruncatefile` attempts `dirfwstat` length update, falls back to manual truncate/extend behavior when needed, and writes zero blocks for extension.
- `smbcomwrite` handles legacy write, including zero-count truncate-at-offset.
- `smbcomwriteandx` handles AndX write with 32-bit or 64-bit offset, data offset validation, write, response, and optional chaining.

Interactions:
- Uses fid map, shared `SmbFile` descriptors, Plan 9 `seek`, `write`, `pwrite`, `pread`, `dirfstat`, and `dirfwstat`.

Notable details:
- Manual truncation beyond 256 KiB is reported unimplemented.
- Directory fids are rejected through `ioallowed`.
