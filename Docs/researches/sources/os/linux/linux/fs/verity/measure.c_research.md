# File Research: sources/os/linux/linux/fs/verity/measure.c

## Purpose
Implements APIs to retrieve the fs-verity digest enforced for a file, plus an optional BPF LSM kfunc for digest access.

## Main Functions
- `fsverity_ioctl_measure()`: handles `FS_IOC_MEASURE_VERITY`, validates user buffer digest capacity, returns algorithm id, digest size, and file digest.
- `fsverity_get_digest()`: kernel API returning raw digest and fs-verity/hash algorithm identifiers.
- BPF support under `CONFIG_BPF_SYSCALL`:
  - `bpf_get_fsverity_digest()`: fills a dynptr with `struct fsverity_digest` and digest bytes.
  - `bpf_get_fsverity_digest_filter()`: restricts kfunc use to BPF LSM programs.
  - `fsverity_init_bpf()`: registers the kfunc id set.

## Important Design Points
- Callers must use the algorithm id with the digest; comments warn that digest bytes alone are not meaningful.
- Ioctl returns `-ENODATA` for non-verity files and `-EOVERFLOW` if the user-provided digest area is too small.
- BPF dynptr output is zero-filled past the digest when larger than needed.
- BPF kfunc is LSM-only to avoid recursion.

## Cross-File Relationships
- Reads cached `fsverity_info` created by `open.c`.
- Uses hash algorithm table from `hash_algs.c`.
- Exported APIs are used by filesystems, IMA/LSM, and other kernel consumers.

## Risks / Review Notes
- Userspace ABI requires writing the header before digest data and preserving exact error behavior.
- BPF dynptr alignment and sizing checks are important for verifier/runtime safety.
