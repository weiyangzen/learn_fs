# File Research: sources/os/bsd/freebsd-src/sys/sys/kerneldump.h

Defines kernel dump on-disk/header ABI and kernel dump helper declarations. Dump headers are stored in network byte order, with `dtoh*`/`htod*` macros depending on host endian.

`struct kerneldumpheader` contains magic, architecture, version, arch version, dump length/time, encrypted key size, block size, hostname, version string, panic string, compression, dump extent, and parity. Supported compression values are none/gzip/zstd; encryption values are none/AES-256-CBC/ChaCha20. `struct kerneldumpkey` stores encryption metadata and variable encrypted key bytes.

Kernel declarations cover minidumps, generic dumps, physical-address chunk iteration, buffered dump writes, generated physical-address helpers, progress reporting, live dump start via device or vnode, and live dump eventhandler hooks.
