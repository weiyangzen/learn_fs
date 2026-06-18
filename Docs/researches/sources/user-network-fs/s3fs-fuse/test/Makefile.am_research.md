# sources/user-network-fs/s3fs-fuse/test/Makefile.am

## Purpose
Automake test/build definition for the s3fs-fuse integration test directory.

## Important APIs, Types, And Control Flow
Declares `TESTS=small-integration-test.sh`, lists distributed helper scripts/configs in `EXTRA_DIST`, and builds no-install helper binaries: `junk_data`, `write_multiblock`, `mknod_test`, `truncate_read_file`, and `cr_filename`. The `clang-tidy` target runs static analysis over these helper C++ sources with configured C++ standard and dependency flags.

## State And Persistence
Build products are local test binaries. Running `make check` delegates to the shell test suite and its generated runtime state.

## Dependencies And Integration Points
Depends on Automake variables, configured `@CPP_VERSION@`, and project `DEPS_CFLAGS`/`CPPFLAGS`. Integrates helper binaries used by `integration-test-main.sh`.

## Risks And Test Signals
Only `small-integration-test.sh` is in `TESTS`; broader behavior depends on environment variable `ALL_TESTS`. Missing helper source declarations would break integration tests at runtime. `make check -C test/` is the primary signal.
