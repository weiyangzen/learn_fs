# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/old_xdr_subs.h

This legacy header defines XDR conversion macros for older NFS code. It covers unsigned 32-bit conversion, NFSv2 time conversion, NFSv3 time conversion, and 64-bit hyper conversion using explicit 32-bit network-order words.

Key contents:
- `fxdr_unsigned(t, v)` and `txdr_unsigned(v)` wrappers around `ntohl` and `htonl`.
- `fxdr_nfsv2time()` and `txdr_nfsv2time()` for converting between NFSv2 seconds/microseconds and `timespec` seconds/nanoseconds, including the legacy `0xffffffff` sentinel behavior.
- `fxdr_nfsv3time()` and `txdr_nfsv3time()` for NFSv3 seconds/nanoseconds.
- `fxdr_hyper()` and `txdr_hyper()` for converting 64-bit protocol quantities to and from two 32-bit words.

Important behavior:
- The macros avoid assuming native alignment for 64-bit values, which is important for XDR buffers.
- The older header lacks the NFSv4 time helpers present in `xdr_subs.h`.

Research notes:
- This file exists because the import script renamed the old FreeBSD `nfs/xdr_subs.h` to `old_xdr_subs.h` before merging old and new NFS directories.
- Use this when reading legacy NFS code; use `xdr_subs.h` for the newer common stack.
