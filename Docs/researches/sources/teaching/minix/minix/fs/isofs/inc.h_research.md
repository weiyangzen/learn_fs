# File Research: sources/teaching/minix/minix/fs/isofs/inc.h

This is the shared include header for isofs.

Role:
- Defines `_SYSTEM`.
- Includes MINIX, fsdriver, libminixfs, bdev, libc, dirent, and assert headers.
- Defines `b_data(bp)` as a `char *` view over buffer data.
- Includes local `const.h`, `proto.h`, `super.h`, and `glo.h`.

Impact:
- Gives all isofs modules a common environment and the same raw buffer accessor.
