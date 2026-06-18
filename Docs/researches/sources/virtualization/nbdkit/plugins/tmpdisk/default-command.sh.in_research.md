# File Research: sources/virtualization/nbdkit/plugins/tmpdisk/default-command.sh.in

Template shell command embedded into the `tmpdisk` plugin as the default disk creation command.

Key behavior:
- Defaults `type` to `ext4` if unset.
- Chooses mkfs flags by filesystem type:
  - `ext?`: `-F`
  - `*fat`/`msdos`: `-I`
  - `ntfs`: `-Q -F` and label option `-n`
  - `xfs`: `-f`
- Creates the backing disk file with substituted `__TRUNCATE__ -s $size "$disk"`.
- Runs `mkfs -t "$type"` with optional label, using `-L` by default or `-n` for NTFS.

Inputs supplied by `tmpdisk.c`:
- `disk`: path to generated temporary backing file.
- `size`: requested virtual disk size.
- Optional user-provided shell variables such as `type` and `label`.

Notes:
- The file is not run directly from source; `Makefile.am` converts it into a C string.
- User-configured variables are shell-quoted by `tmpdisk.c` before this command runs.
