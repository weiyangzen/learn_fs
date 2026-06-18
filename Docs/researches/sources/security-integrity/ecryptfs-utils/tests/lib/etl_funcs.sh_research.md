## sources/security-integrity/ecryptfs-utils/tests/lib/etl_funcs.sh

Purpose: Shared bash library for eCryptfs tests. It centralizes key creation/unlinking, disk-image creation, lower-filesystem mounting, eCryptfs mounting, capacity estimation, temporary test-directory creation/removal, and mapping an upper inode to its lower path.

Important APIs and functions: `etl_add_fekek_passphrase`, `etl_add_fnek_passphrase`, `etl_add_keys`, `etl_unlink_key_sig`, `etl_unlink_fekek`, `etl_unlink_fnek`, `etl_unlink_keys`, `etl_create_disk`, `etl_remove_disk`, `etl_load_ecryptfs`, `etl_construct_lmount_opts`, `etl_lmount`, `etl_lumount`, `etl_lmax_filesize`, `etl_mount_i`, `etl_umount_i`, `etl_umount`, `etl_create_test_dir`, `etl_remove_test_dir`, `etl_find_lower_path`.

Control flow and state: Defaults define passphrases, salts, lower filesystem options, and eCryptfs mount options. Functions communicate through exported `ETL_*` variables such as `ETL_FEKEK_SIG`, `ETL_FNEK_SIG`, `ETL_DISK`, `ETL_LMOUNT_SRC/DST`, and `ETL_MOUNT_SRC/DST`. Persistent state includes temporary disk images, mounted lower/upper filesystems, and kernel keyring entries.

Dependencies and risks: Requires bash, keyctl, modprobe, mkfs, mount/umount, df, find, stat, and root privileges for many paths. A notable bug-risk is tests like `[ -n "ETL_FNEK_SIG" ]` and `[ -z "lmount" ]` using literals rather than variables, which can force filename-encryption mount options or skip validation unexpectedly. Integration is broad: most kernel scripts source this file, so regressions cascade across the suite.
