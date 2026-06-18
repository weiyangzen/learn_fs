# sources/test-tools/crashmonkey/ace/xfstestAdapter.py

## Purpose

`xfstestAdapter.py` converts ACE j-lang workloads into xfstests shell tests and matching `.out` files. It supports two j-lang formats: V1 sectioned files with setup/run commands and V2 concise single-command templates with argument option arrays. Its role is to let ACE-generated crash-consistency workloads run in xfstests/flakey infrastructure instead of only through the CrashMonkey C++ harness.

## Important APIs, Types, and Functions

- `FallocTranslate` maps ACE fallocate modes to `$XFS_IO_PROG` commands (`falloc`, `falloc -k`, `fzero`, `fzero -k`, `fpunch`).
- File constants (`FILE_ATTR_KEY`, `WRITE_VALUE`, `MMAPWRITE_VALUE`, `DWRITE_VALUE`) define stable data patterns and xattr names.
- `get_row_from_filename`, `translate_filename`, `parent`, and `is_file_or_dir` translate j-lang names through `common.JLANG_FILES` into `$SCRATCH_MNT/...` paths.
- `State` tracks `opened_files`, `synced_files`, and `data_synced_files`, preserving the invariant that metadata-synced files are data-synced and data-synced files are opened/known.
- `translate_*` functions map individual j-lang operations to shell snippets and update `State`.
- `translate_functions` dispatches V1 command lines, paying attention to prefix ordering (`opendir` before `open`).
- `build_test_v1` translates a sectioned j-lang file into a linear flakey mount script plus `check_consistency`.
- `function_name_from_commands`, `build_command_dependencies`, `build_template_function`, `build_array_lines`, `build_for_loops`, and `add_sync_check_consistency` support concise V2 templated tests.
- `build_test_v2` emits a parameterized shell function and nested option loops.
- `main` selects V1 or V2 based on the first line containing `J2-Lang`, validates test number, creates the output directory, and builds the test.

## Control Flow

For V1, the adapter finds `base_xfstest.sh`, replaces template parameters, reads setup/run j-lang commands, starts with `_mount_flakey`, translates each command while updating consistency state, appends a `check_consistency` command for the currently synced file set, appends `clean_dir`, and writes `<test_number>` plus `<test_number>.out`.

For V2, it finds `base_xfstest_concise.sh`, parses option declarations and exactly one command, builds setup/dependency commands for that command, adds either `do_fsync_check` or a direct `check_consistency`, emits a shell function, emits sorted option arrays with translated file paths, and emits nested loops over all options and fsync targets.

## State and Persistence Behavior

The persistent outputs are two xfstests files under the target path: the executable test body and a `.out` file containing the expected quiet output. `State` is transient but determines the final `check_consistency` arguments for V1. Rename and remove operations deliberately mutate synced/opened sets so the final consistency oracle reflects the crash-persistence model rather than just command execution.

## Dependencies and Integration Points

The adapter depends on `common.JLANG_FILES`, xfstests helpers (`_mount_flakey`, `_pwrite_byte`, `_dwrite_byte`, `_mwrite_byte_and_msync`, `check_consistency`, `clean_dir`, `ensure_file_size_one_block`, `translate_range`, `do_falloc`, `do_fsync_check`), `$XFS_IO_PROG`, `attr`, and the `rename` command. It uses base templates from `../code/tests/ace-base` or the current ACE directory. Generated scripts are intended to be copied into an xfstests suite directory under a filesystem group such as `generic`, `ext4`, `btrfs`, `xfs`, or `f2fs`.

## Risks and Edge Cases

- `is_dir` computes a comparison but does not return it.
- `find_basefile` has an unreachable `print` after `return`.
- `translate_filename` assumes `get_row_from_filename` returns a row; unknown names raise `TypeError`.
- V2 asserts exactly one command, so multi-command concise workloads are unsupported.
- V2 rename dependency uses `create_file(parts[1])` even if the source is a directory option.
- Shell emission is mostly string formatting without quoting; unusual paths or options can break scripts, though ACE's synthetic names are constrained.
- `State.rename_file` has special handling for directory renames only for hard-coded dirs `A`, `B`, and `AC` and children `foo`, `bar`.

## Test Signals

Signals include generated executable and `.out` files, successful xfstests dry runs, V1 fixtures covering every `translate_*` function, V2 fixtures covering each command type and fsync loop generation, and consistency-command assertions for operations that only sync data (`fdatasync`) versus metadata (`fsync`/`sync`). Unknown file names should be tested as failures because translation depends on `JLANG_FILES`.
