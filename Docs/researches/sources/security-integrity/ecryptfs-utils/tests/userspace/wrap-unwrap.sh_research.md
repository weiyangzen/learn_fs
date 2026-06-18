## sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap.sh

Purpose: Userspace wrapper for libecryptfs passphrase wrapping/unwrapping regression tests. It creates a temporary test path and passes it to the C helper.

Important APIs and functions: sources `etl_funcs.sh`, uses `etl_create_test_dir`, runs `${test_script_dir}/wrap-unwrap/test`, cleanup calls `etl_remove_test_dir`. Control flow does not mount eCryptfs; it relies on the helper writing a wrapped passphrase file at the supplied path.

State and persistence: Creates a temporary directory under the default or environment-provided parent and a file path used by the C helper; cleanup removes the directory. Dependencies are bash, the helper binary, and libecryptfs. Integration is distributed as a non-installed script and can be run by the custom harness. Risk: `test_dir` is used in cleanup before explicit initialization, but empty values are harmless in `etl_remove_test_dir`.
