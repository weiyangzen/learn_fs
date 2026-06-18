# File Research: sources/os/bsd/netbsd-src/lib/librmt/rmtlib.c

Read completely: 896 lines.

Implements a remote tape compatibility library that can replace `open`, `read`, `write`, `lseek`, `ioctl`, and related file operations. Remote devices are detected by paths containing `:/dev/`, opened by forking `rsh` to run `/etc/rmt`, and represented to callers as small internal unit numbers plus `REM_BIAS` 128.

The private protocol helpers send textual remote-tape commands (`O`, `C`, `R`, `W`, `L`, `I`, `S`), parse `A` success and `E`/`F` error replies, ignore `SIGPIPE` around pipe writes, and abort connections on fatal or protocol errors. Up to four remote units are tracked through parent-to-child and child-to-parent pipe arrays.

Public wrappers dispatch local descriptors to normal syscalls and remote descriptors to protocol operations. Some operations such as `dup`, `fstat`, `stat`, `lstat`, and `fcntl` are unsupported remotely and return `EOPNOTSUPP`. The MTIOCGET path reads raw `struct mtget` bytes and contains historical byte-swap logic with acknowledged portability assumptions.
