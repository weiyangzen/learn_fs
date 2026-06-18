# File Research: sources/teaching/minix/minix/fs/mfs/fs.h

This is the umbrella header for the MFS service. It marks the build as system code with `_SYSTEM`, sets a `VERBOSE` initialization flag, and includes the MINIX, libc, system utility, and fsdriver headers required by most service source files.

After the platform and fsdriver includes, it pulls in the local MFS headers in the order needed by the service: `mfsdir.h`, `const.h`, `type.h`, `proto.h`, and `glo.h`. As a result, most `.c` files include `fs.h` first and receive the common constants, on-disk type declarations, prototypes, and global declarations.
