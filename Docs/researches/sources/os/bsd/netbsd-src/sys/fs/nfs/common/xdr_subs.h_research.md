# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/xdr_subs.h

This header provides XDR conversion macros for the new NFS stack. It is the modern counterpart to `old_xdr_subs.h`, adding NFSv4 time conversion while retaining unsigned, NFSv2/NFSv3 time, and 64-bit hyper conversion helpers.

Key contents:
- `fxdr_unsigned(t, v)` and `txdr_unsigned(v)` for 32-bit network/native conversion.
- `fxdr_nfsv2time()` and `txdr_nfsv2time()` for v2 seconds/microseconds to `timespec`.
- `fxdr_nfsv3time()` and `txdr_nfsv3time()` for v3 seconds/nanoseconds.
- `fxdr_nfsv4time()` and `txdr_nfsv4time()` for v4 high-seconds/seconds/nanoseconds. The decode macro ignores high seconds and clamps nanoseconds with modulo `1000000000`.
- `fxdr_hyper()` and `txdr_hyper()` for unaligned 64-bit values represented as two 32-bit XDR words.

Important behavior:
- All conversions use `ntohl`/`htonl`, relying on them being optimized away on big-endian systems where appropriate.
- The macros deliberately avoid direct 64-bit loads/stores from XDR buffers because alignment is not guaranteed.
- NFSv4 time encoding sets `nfsv4_highsec` to zero, so it only represents times fitting in the low seconds word.

Research notes:
- This file is used anywhere common NFS code converts between mbuf/XDR words and kernel scalar/time types.
- Review time conversion behavior carefully for overflow, high-second handling, and invalid nanosecond values.
