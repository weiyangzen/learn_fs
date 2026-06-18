## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir.sh

Purpose: Shell harness for the directory mmap negative test. It mounts an eCryptfs filesystem and invokes the sibling C probe against a temporary directory.

Important APIs and functions: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `${test_script_dir}/mmap-dir/test`, cleanup trap with unmount/key unlink. Control flow is standard for eCryptfs kernel tests: prepare keys and mounts, create test directory, run C test with that directory, propagate status.

State and persistence: Only transient mount/key/test-directory state. Dependencies include eCryptfs mountability and the C binary. Integration is with kernel bug LP 400443 coverage in the C file. Risks are mostly setup-related; because the target operation is a negative syscall check, environment failures are separated by the C test’s `TEST_ERROR` path where possible.
