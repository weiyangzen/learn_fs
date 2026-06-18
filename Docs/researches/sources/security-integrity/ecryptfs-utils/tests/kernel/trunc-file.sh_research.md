## sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file.sh

Purpose: Shell harness for a file truncation stress test over eCryptfs. It computes a conservative lower-filesystem capacity, caps it at 16,384 KiB, then asks the C test to exercise truncation and extension.

Important APIs and functions: `etl_lmax_filesize`, `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, and `${test_script_dir}/trunc-file/test`. Control flow prepares mount state, chooses block count, runs the C test on `test.img`, and cleans up through the trap.

State and persistence: Transient keyring, mounts, temp directory, and test image. Dependencies include enough disk space and correct lower filesystem reporting; `etl_lmax_filesize` adjusts for btrfs/xfs quirks. Integration is a kernel filesystem data-integrity test. Risks include long runtime or ENOSPC on small lower filesystems; the cap and helper slop logic bound the workload.
