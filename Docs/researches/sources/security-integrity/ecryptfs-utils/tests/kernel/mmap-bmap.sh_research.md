## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap.sh

Purpose: Shell harness that verifies block mappings reported through the eCryptfs upper file are a subset of the underlying lower encrypted file’s block mappings. It writes a 1 MiB file, locates the corresponding lower inode, and invokes the C `mmap-bmap/test` comparator.

Important APIs and functions: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `dd`, `etl_find_lower_path`, and remount sequence `etl_umount`/`etl_mount_i`. Control flow mounts, writes the test file, finds the lower path using inode lookup, runs the comparator with lower and upper paths, then remounts before exiting.

State and persistence: Creates mounted test state, a 1 MiB file, and keyring entries; cleanup removes mounts, keys, and the test directory. Dependencies include FIBMAP-capable filesystems, root privileges, and the sibling C test. Risk: filesystems that do not support `FIBMAP` may zero mappings in the C code, changing signal quality; block allocation behavior can vary by lower filesystem.
