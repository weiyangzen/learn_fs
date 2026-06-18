# File Research: sources/os/linux/linux-stable/fs/verity/Makefile

Builds the fs-verity core from `enable.o`, `hash_algs.o`, `init.o`, `measure.o`, `open.o`, `pagecache.o`, `read_metadata.o`, and `verify.o` when `CONFIG_FS_VERITY` is enabled. `signature.o` is included only when builtin signature support is configured.

This mirrors the subsystem split: enabling and Merkle tree construction, hash algorithm support, initialization/logging, digest measurement, open-time descriptor loading, generic Merkle pagecache helpers, metadata read ioctl support, read-time verification, and optional PKCS#7 signature validation.
