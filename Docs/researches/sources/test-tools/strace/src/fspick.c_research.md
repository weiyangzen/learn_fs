# sources/test-tools/strace/src/fspick.c

Decoder for `fspick`. It prints directory fd, pathname, and `fspick_flags`, returning a filesystem context fd. State is only arguments. Dependencies are `<linux/mount.h>`, dirfd/path printers, and xlat flags. Risks include `AT_EMPTY_PATH`-like semantics, null paths, and newly added flags. Tests should cover path and fd-based picking, empty paths, unknown flags, bad pointers, and fd-return formatting.
