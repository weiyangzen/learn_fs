# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-win32.c

Implements the Windows variant of host filesystem device `#U/fs`.

Key behavior:
- Disables Windows Unicode APIs and uses narrow-character `FindFirstFile`/`FindNextFile`.
- Uses `base = "c:/."`.
- Mirrors the POSIX implementation’s Plan 9 device operations: attach, walk, stat, open, create, read, write, remove, and wstat.
- Opens regular files in binary mode with `_O_BINARY`.
- Provides a local `DIR` abstraction around Windows file enumeration.
- Implements no-op `chown`.
- Packs directory entries into Plan 9 `Dir` records with owner/group set to `"unknown"`.

Important interfaces:
- Same `fsqid`, `fspath`, `fsdirread`, and `fsomode` structure as POSIX variant.
- Custom `opendir`, `readdir`, `rewinddir`, and `closedir`.

Notable risks:
- Narrow-character Windows API use means non-ASCII paths are not represented correctly.
- `opendir` appends `*.*`, matching Windows-era conventions.
- Uses fixed-size path buffers and simple string concatenation.
