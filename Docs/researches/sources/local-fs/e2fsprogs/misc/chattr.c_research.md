# File Research: sources/local-fs/e2fsprogs/misc/chattr.c

## Purpose
Implements `chattr`, changing Linux filesystem inode flags, generation/version, and project ID.

## Main Behavior
- Parses `+flags`, `-flags`, and `=flags`, plus `-R`, `-V`, `-f`, `-v version`, and `-p project`.
- Maps option letters to ext filesystem flags through `flags_array`.
- `change_attributes()` reads current flags, applies set/add/remove semantics, clears `EXT2_DIRSYNC_FL` on non-directories, writes flags, and optionally writes version/project.
- Recursion uses `iterate_on_dir()` and skips `.`/`..`.

## Integration
Uses e2p helpers `fgetflags`, `fsetflags`, `fsetversion`, `fsetproject`, `print_flags`, and directory iteration support.

## Risks / Notes
- `=` is mutually exclusive with `+` and `-`.
- The same flag cannot be both added and removed.
- Symlink handling relies on `lstat`, but flag operations are path-based through e2p helpers.
