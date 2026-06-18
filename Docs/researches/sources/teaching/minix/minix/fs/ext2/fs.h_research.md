# File Research: sources/teaching/minix/minix/fs/ext2/fs.h

This is the master ext2 filesystem-server header.

Role:
- Defines `_SYSTEM` for MINIX system headers.
- Pulls in MINIX, libc, fsdriver, and local ext2 headers.
- Includes `const.h`, `type.h`, `proto.h`, and `glo.h`.
- Defines `ext2_debug` as `printf`.

Impact:
- Most ext2 `.c` files include this header first, giving them shared constants, types, prototypes, globals, and fsdriver access.
