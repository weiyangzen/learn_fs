## sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir.sh

Purpose: Shell harness for verifying `read()` on an eCryptfs directory returns the expected POSIX-style error. It prepares a mounted encrypted test directory and executes `read-dir/test`.

Important APIs and functions: same eCryptfs helper flow as neighboring tests: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, cleanup via trap. Control flow sets up the mount, runs the C test on the temp directory, captures its exit code, and exits.

State and persistence: Transient keys, lower/upper mounts, and a test directory only. Dependencies are bash, keyctl/mount tooling through `etl_funcs.sh`, and the sibling compiled probe. Integration covers Ubuntu bug 719691. Risks are setup and errno-policy sensitivity; the C probe separates usage/open errors from semantic failures.
