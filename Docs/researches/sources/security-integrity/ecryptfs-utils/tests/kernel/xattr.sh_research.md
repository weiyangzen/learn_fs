## sources/security-integrity/ecryptfs-utils/tests/kernel/xattr.sh

Purpose: Shell harness for extended attribute behavior through eCryptfs. It creates a regular file in an encrypted mount and runs the sibling C test to set/list/get/remove `user.*` attributes.

Important APIs and functions: standard `etl_*` setup/cleanup, simple file creation with shell redirection, `${test_script_dir}/xattr/test`, remount sequence after the probe. Control flow mounts, writes initial file contents, runs the C xattr check, stores its result, attempts removal, remounts, and exits.

State and persistence: Creates a test file and transient xattrs; keys and mounts are cleaned. Dependencies include lower filesystem `user_xattr` support, which `etl_funcs.sh` enables for ext2/3/4 defaults. Integration is a kernel metadata test. Risk: the script removes `$test_file1` rather than `$test_file`, likely a typo, but trap cleanup removes the enclosing directory. Remount after xattr operations provides some persistence pressure.
