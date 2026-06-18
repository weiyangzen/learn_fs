# File Research: sources/os/linux/linux-stable/fs/verity/measure.c

Implements digest measurement APIs for fs-verity files. `fsverity_ioctl_measure()` serves `FS_IOC_MEASURE_VERITY`: it requires cached verity info, checks that the user buffer’s digest capacity is large enough, returns algorithm and digest size, then copies the enforced file digest to userspace.

`fsverity_get_digest()` is an exported in-kernel helper that copies the raw digest and optionally returns both fs-verity and generic `HASH_ALGO_*` algorithm identifiers. The comments emphasize that callers must use an algorithm id because raw digest bytes alone are not meaningful.

When BPF syscall support is enabled, the file registers the LSM-only kfunc `bpf_get_fsverity_digest()`, which writes a `struct fsverity_digest` plus digest bytes into a BPF dynptr and zero-fills extra output space. A filter rejects non-LSM program types to avoid recursion.
