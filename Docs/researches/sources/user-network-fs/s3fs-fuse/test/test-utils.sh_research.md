# sources/user-network-fs/s3fs-fuse/test/test-utils.sh

## Purpose
This Bash helper library supports the s3fs-fuse integration test suite. It centralizes test constants, portable command selection, file/xattr helpers, suite execution, S3 HTTP helpers, mount-process inspection, OS timing waits, and workaround wrappers for platform-specific behavior.

## Important APIs, Types, and Functions
The file exports shell variables such as `TEST_TEXT`, `TEST_TEXT_FILE`, `TEST_DIR`, `BIG_FILE_BLOCK_SIZE`, `BIG_FILE_LENGTH`, `STAT_BIN`, `STDBUF_BIN`, `TRUNCATE_BIN`, and `SHA256SUM_BIN`. The xattr wrappers are `find_xattr`, `get_xattr`, `set_xattr`, and `del_xattr`, switching between macOS `xattr` and Linux `getfattr`/`setfattr`. Metadata helpers include `get_inode`, `get_size`, `get_ctime`, `get_mtime`, `get_atime`, `get_permissions`, `get_user_and_group`, and `check_file_size`.

Test lifecycle helpers include `mk_test_file`, `rm_test_file`, `mk_test_dir`, `rm_test_dir`, `cd_run_dir`, `clean_run_dir`, `init_suite`, `add_tests`, `report_pass`, `report_fail`, `describe`, and `run_suite`. S3 helpers include `s3_head`, `s3_mb`, `s3_cp`, and `check_content_type`; process and platform helpers include `wait_for_port`, `s3fs_args`, `wait_ostype`, and `cp_avoid_xattr_err`.

## Control Flow
Top-level initialization enables `errexit` and `pipefail`, sets locale to `en_US.UTF-8`, selects GNU command names on Darwin, and adjusts `STAT_BIN` if the installed stat supports cache-bypass flags. `run_suite` creates a unique run directory below `TEST_BUCKET_MOUNT_POINT_1`, iterates over `TEST_LIST`, rewrites per-test filenames with a sequential suffix, runs each test in a subshell with `errexit`, records pass/fail state, cleans the run directory, prints a summary, and returns failure if any test failed.

## State and Persistence
State is mostly shell-global: test lists, pass/fail arrays, mutable filename variables, S3 credentials inherited from the environment, and the current working directory. The script creates and deletes files/directories in the mounted bucket, creates temporary header/body files with `mktemp`, and performs real HTTP operations against the configured S3 endpoint. No long-lived local database is used.

## Dependencies and Integration Points
The helpers integrate with FUSE-mounted s3fs paths, curl AWS SigV4 support, S3Proxy or compatible S3 endpoints, GNU coreutils on macOS, filesystem xattr tools, `df`, `ps`, and test binaries/scripts that source this file. `s3_cp` deliberately defaults `Content-Type: application/octet-stream` unless a caller supplies one.

## Risks and Test Signals
Risks include destructive `rm -rf` in `clean_run_dir`, command behavior differences between Linux and macOS, locale availability, credential leakage through curl/process environments, direct `/dev/tcp` probing, and fragile parsing of HTTP headers and `df` output. Strong test signals are full suite pass/fail summaries, `check_file_size` comparing metadata and data length, `check_content_type` using S3 HEAD, xattr round-trips, and platform CI coverage for Linux/macOS branches.
