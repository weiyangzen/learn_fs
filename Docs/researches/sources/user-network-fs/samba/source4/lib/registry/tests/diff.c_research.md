# sources/user-network-fs/samba/source4/lib/registry/tests/diff.c

## Purpose

`tests/diff.c` is the torture suite for registry diff generation and application. It verifies both PReg and `.reg` patch save paths against local LDB-backed registries.

## Important APIs, Types, and Functions

`struct diff_tcase_data` stores two registry contexts, diff callbacks, callback data, temp directory, and generated patch filename. `diff_setup_tcase()` builds the source and target registries. `diff_setup_preg_tcase()` and `diff_setup_dotreg_tcase()` select the output format. Tests include `test_generate_diff()`, `test_diff_apply()`, `test_generate_diff_key_add()`, and `test_generate_diff_key_null()`, though the add-key test currently returns before exercising assertions.

## Control Flow

Setup creates two local registry contexts, mounts HKLM and HKCU LDB hives for each, populates r1 with `HKCU\Network\L`, populates r2 with `HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer`, and writes a `NoDrives` DWORD. Format-specific setup initializes callbacks with either `reg_preg_diff_save()` or `reg_dotreg_diff_save()`. The generate test calls `reg_generate_diff()`. The apply test applies the generated patch to r1 and then walks the expected HKLM path.

## State and Persistence Behavior

All registry state is created in a torture temp directory. The patch file is persisted as `test.pol` or `test.reg` and then applied to mutate r1. Test lifetime and cleanup are managed by the torture context.

## Dependencies and Integration Points

The suite uses the registry API, LDB hive backend, PReg and dotreg diff writers, the generic diff engine, winreg constants, loadparm/event context from torture, and Samba torture assertion helpers. It is included in the `torture_registry` subsystem by `wscript_build`.

## Risks and Edge Cases

The suite checks only one high-level creation path and one value, so delete operations, value data comparisons after apply, and error handling remain lightly covered. The early return in `test_generate_diff_key_add()` disables an intended direct callback test. Because apply correctness is inferred by opening a path, a broken value update could pass.

## Test Signals

Passing PReg and dotreg tcase runs signal that diff callbacks can write files, `reg_generate_diff()` emits a usable patch, and `reg_diff_apply()` can create missing nested keys. Stronger signals would assert value content, deletion markers, no-op diffs, and malformed patch rejection.

Source-read signal: reviewed complete local file (291 lines).
