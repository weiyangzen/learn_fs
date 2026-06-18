# File Research: sources/virtualization/libguestfs/daemon/grep.c

Wraps `grep` and `zgrep` variants.

Important behavior:
- Shared `grep()` helper validates incompatible `extended && fixed`.
- Opens the guest file under `CHROOT_IN`, then copies that fd to command stdin with `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- Treats grep exit status `1` as “no matches” and returns an empty list.
- Supports API-era aliases: `grep`, `egrep`, `fgrep`, case-insensitive variants, and compressed variants.

Filesystem relevance: content search is performed through host/appliance command execution while file access stays chroot-scoped.
