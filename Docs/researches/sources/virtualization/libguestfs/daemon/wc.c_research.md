# File Research: sources/virtualization/libguestfs/daemon/wc.c

## Role
Implements line, word, and byte count actions for guest files.

## Main Operation
- `wc()` opens a guest path inside chroot and runs `wc` with the requested flag, feeding the file descriptor to stdin through `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- Parses the leading integer from command output.
- `do_wc_l()`, `do_wc_w()`, and `do_wc_c()` provide line, word, and byte counts.

## Filesystem/Storage Relevance
Provides simple file content metrics without exposing guest paths directly to host commands.
