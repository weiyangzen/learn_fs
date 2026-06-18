# sources/user-network-fs/samba/source4/lib/registry/tests/registry.c

## Purpose

`tests/registry.c` tests the higher-level registry API over a local registry context with a mounted HKCR LDB hive. It verifies predefined-key resolution, absolute path helpers, key/value operations, enumeration, flush, metadata, and security descriptors.

## Important APIs, Types, and Functions

`setup_local_registry()` opens a local registry, creates a temp LDB hive, and mounts it as `HKEY_CLASSES_ROOT`. Test functions include `test_get_predefined()`, `test_get_predefined_unknown()`, `test_predef_key_by_name()`, `test_create_subkey()`, `test_create_nested_subkey()`, `test_key_add_abs()`, `test_key_add_abs_top()`, `test_del_key()`, `test_flush_key()`, `test_query_key()`, `test_query_key_nums()`, `test_list_subkeys()`, `test_set_value()`, `test_security()`, `test_get_value()`, `test_del_value()`, and `test_list_values()`.

## Control Flow

Most tests first call `create_test_key()` to open HKCR and create a named subkey. They then dispatch through registry-level wrappers such as `reg_key_add_name()`, `reg_open_key()`, `reg_key_get_info()`, `reg_val_set()`, `reg_key_get_value_by_name()`, `reg_key_get_value_by_index()`, `reg_del_value()`, `reg_key_del()`, `reg_get_sec_desc()`, and `reg_set_sec_desc()`. The suite builder installs all tests in one local tcase.

## State and Persistence Behavior

The mounted HKCR hive is a temp LDB file. Tests mutate it by adding keys and values and deleting selected entries. Some tests rely on independent names to avoid clashes in the shared fixture context. Default unnamed values are explicitly tested with empty value names.

## Dependencies and Integration Points

The file exercises `registry.h` APIs, the local registry backend, LDB hive backend, winreg constants, security descriptor helpers, and torture infrastructure. It complements `tests/hive.c` by testing path parsing and predefined root behavior rather than raw hive calls.

## Risks and Edge Cases

Duplicate test names appear in `tcase_add_tests()` for some cases, which may affect reporting clarity. The suite mounts only HKCR, so multi-hive behavior and other predefined roots are not covered. The tests do not inspect persistence after process teardown, notification/load/unload paths, or RPC-specific behavior.

## Test Signals

Passing this suite signals correct local mounted-registry operation for common CRUD and lookup workflows. Additional signal would come from absolute delete tests, multi-root mounting, case-insensitive predefined names beyond HKCR, path traversal edge cases, and reopened-hive persistence checks.

Source-read signal: reviewed complete local file (645 lines).
