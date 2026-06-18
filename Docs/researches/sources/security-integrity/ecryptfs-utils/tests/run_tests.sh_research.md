## sources/security-integrity/ecryptfs-utils/tests/run_tests.sh

Purpose: Main eCryptfs test-suite harness. It selects kernel and/or userspace tests by category or explicit list, prepares lower/upper mount points and optional disk images/devices, runs test scripts, and prints pass/fail summary.

Important APIs and functions: `run_tests_cleanup`, `run_tests`, `run_kernel_tests_on_existing_device`, `run_kernel_tests_on_created_disk_image`, `usage`, `getopts`, sourcing `kernel/tests.rc` and `userspace/tests.rc`, plus `etl_create_disk`/`etl_remove_disk`. Control flow validates mutually exclusive `-b` disk-image vs `-d` device modes, validates mount paths, creates temp mountpoints if needed, exports `ETL_LMOUNT_DST`, `ETL_MOUNT_SRC`, and `ETL_MOUNT_DST`, builds test lists from categories, and runs scripts while counting failures.

State and persistence: May create temporary mount directories and disk images; cleanup removes only directories it created and any ETL disk. Dependencies include bash, root privileges for kernel tests, mountable lower filesystems, and test rc files. Risks include destructive device usage via `-d`, category variable expansion with `eval`, and counting/reporting based only on script exit status.
