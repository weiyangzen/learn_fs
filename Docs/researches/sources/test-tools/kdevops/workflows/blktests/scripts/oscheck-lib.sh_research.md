# sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-lib.sh

## Purpose
Shared OS/kernel compatibility and expunge-list library for blktests wrappers.

## Important APIs, Types, and Functions
Important functions include `oscheck_lib_init_vars`, `validate_run_group`, `oscheck_lib_set_run_group`, `oscheck_read_osfile_and_includes`, `oscheck_distro_kernel_check`, `oscheck_add_expunge_no_dups`, `oscheck_get_group_files`, `oscheck_handle_group_expunges`, `oscheck_lib_set_expunges`, and `oscheck_lib_mktemp`. Important state includes `OSCHECK_ID`, `VERSION_ID`, `RUN_GROUP`, `EXPUNGE_TESTS`, and `EXPUNGE_FLAGS`.

## Control Flow
Initialization sets defaults and valid groups. OS detection sources distro helpers and optional distro-specific functions. Kernel checks may mark custom kernels or exit for distro-kernel queries. Expunge handling combines special hooks, result-derived failures, kernel files, distro-version files, and generic `any` failures.

## State and Persistence Behavior
Exports shell variables for callers. Reads `/etc/os-release`, helper scripts, result trees, expunge files, and blktests test paths without writing durable state.

## Dependencies and Integration Points
Used by `oscheck.sh` and `oscheck-get-failures.sh`; integrates with `../osfiles`, `../expunges`, and upstream blktests `tests/`.

## Risks and Edge Cases
Many unquoted expansions are path-fragile. Duplicate detection via grep over a whitespace string can conflate related IDs. `eval` of `ID=` from os-release trusts file content. Some messages use `$GROUP` instead of `$RUN_GROUP`.

## Test Signals
Shell-test synthetic OS files/helpers/expunges, custom kernel mode, each valid group, missing test files, duplicate IDs, fallback expunge paths, and no-expunge cases.
