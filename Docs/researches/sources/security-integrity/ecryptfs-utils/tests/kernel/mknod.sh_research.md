## sources/security-integrity/ecryptfs-utils/tests/kernel/mknod.sh

Purpose: Kernel filesystem sanity test that verifies special-device node creation through an eCryptfs mount preserves device major/minor values. It creates a character device `c 1 7` inside a temporary encrypted test directory and checks `stat -c%t:%T`.

Important APIs and functions: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `mknod`, `stat`, cleanup via `etl_remove_test_dir`, `etl_umount`, `etl_lumount`, `etl_unlink_keys`. Control flow prepares keys, lower mount, eCryptfs mount, creates a test directory, performs `mknod`, validates `1:7`, removes the node, and exits through cleanup.

State and persistence: Creates keyring entries, lower/upper mounts, and one transient special file. Dependencies include root privileges or `CAP_MKNOD`, eCryptfs, mount helpers, and a lower filesystem allowing device nodes. Integration is under kernel tests. Risks are privilege and mount-option sensitivity; failures may reflect environment policy rather than eCryptfs metadata behavior.
