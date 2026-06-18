# sources/security-integrity/ecryptfs-utils/src/libecryptfs/sysfs.c

## Purpose
Reads the eCryptfs kernel module feature/version mask from sysfs and exposes helpers that test individual feature bits. This lets userspace tailor mount prompts and options to kernel support.

## Important APIs, types, and functions
- `get_sysfs_mountpoint` scans `/etc/mtab` for a `sysfs` mount and falls back to `/sys`.
- `ecryptfs_get_version` reads `<sysfs>/fs/ecryptfs/version`, attempting `/sbin/modprobe ecryptfs` if the file is missing.
- `ecryptfs_version_str_map` maps feature bits to human-readable labels.
- `ecryptfs_supports_passphrase`, `ecryptfs_supports_pubkey`, `ecryptfs_supports_plaintext_passthrough`, `ecryptfs_supports_hmac`, `ecryptfs_supports_filename_encryption`, `ecryptfs_supports_policy`, and `ecryptfs_supports_xattr` return bit-test results.

## Control flow
Version loading first discovers the sysfs mountpoint size, allocates a buffer, reads the mountpoint, builds the eCryptfs version path, opens it, optionally modprobes and retries, reads up to 16 bytes, and parses it with `atoi`. Feature helpers are direct bit masks over the returned integer.

## State and persistence behavior
Reads `/etc/mtab` and sysfs. It may trigger module loading through `/sbin/modprobe ecryptfs`, which changes kernel module state. No user files are written.

## Dependencies and integration points
`module_mgr.c` uses the feature helpers to decide which mount-option nodes to include. Mount helpers use `ecryptfs_get_version` before graph processing.

## Risks and edge cases
Using `/etc/mtab` can be less reliable than `/proc/mounts` on systems where it is stale or absent. `atoi` does not validate trailing garbage or overflow. A failed version read collapses to `-EINVAL`, losing precise errno. The hard-coded modprobe path may fail on distributions where `modprobe` lives elsewhere or when callers lack privileges.

## Test signals
Tests can mock mount-table/sysfs paths only with indirection or filesystem namespace setup. Useful checks include fallback to `/sys`, missing version file with failed modprobe, malformed version contents, and each feature helper against known bit masks.
