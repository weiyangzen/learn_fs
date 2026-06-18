# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/xdr_subs.h

`xdr_subs.h` defines low-level XDR conversion helpers for NFS protocol encoding/decoding.

Key contents:
- Defines scalar conversion macros `fxdr_unsigned(t, v)` and `txdr_unsigned(v)` using `ntohl()`/`htonl()`.
- Defines NFSv2 time conversion macros between XDR `struct nfsv2_time` and native `timespec`, with the special `0xffffffff` microsecond value handled as zero on decode and `tv_nsec == -1` encoded as `0xffffffff`.
- Defines NFSv3 time conversion macros using seconds and nanoseconds.
- Defines NFSv4 time conversion macros using high seconds, seconds, and nanoseconds; decode ignores high seconds and clamps nanoseconds modulo 1,000,000,000.
- Defines `fxdr_hyper(f)` to decode an unaligned XDR 64-bit unsigned value from two 32-bit words.
- Defines inline `txdr_hyper(uint64_t f, uint32_t *t)` to encode a 64-bit value into two big-endian 32-bit words.

Important integration points:
- These helpers intentionally avoid assuming alignment, which matters for XDR data inside mbuf chains.
- They are used by attribute parsing, file-size/stat fields, timestamps, and protocol marshalling throughout NFS code.

Research notes:
- The file is small but safety-critical: incorrect conversion affects wire compatibility and attribute correctness.
- Native big-endian systems rely on `ntohl()`/`htonl()` compiling away as appropriate.
