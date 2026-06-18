# File Research: sources/virtualization/libguestfs/daemon/hexdump.c

Wraps `hexdump -C`.

Important behavior:
- Opens the guest file under chroot.
- Copies fd to command stdin with `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- Returns the complete hexdump string.

Filesystem relevance: diagnostic byte-level rendering of guest file contents.
