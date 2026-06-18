# sources/user-network-fs/samba/source4/lib/registry/tests/hive.c

## Purpose

`tests/hive.c` tests the low-level hive API independently of predefined registry mounting. It runs the same behavioral checks against LDB hives and newly created REGF hives.

## Important APIs, Types, and Functions

Fixture setup functions are `hive_setup_ldb()` and `hive_setup_regf()`. Test helpers cover deletion of nonexistent keys, root key info, subkey/value counts, add/delete key, recursive delete, flush, value set/get/list/delete, and security descriptor get/set. The suite builder is `torture_registry_hive()`.

## Control Flow

Each fixture creates a temporary path, removes the directory placeholder, and opens either an LDB hive or REGF file. Tests operate directly on the root `struct hive_key`: adding subkeys with `hive_key_add_name()`, setting DWORD values, querying info, enumerating by index, deleting values and keys, and verifying WERROR results. The security test creates an authenticated-users descriptor, sets it on a subkey, reads it back, then repeats after setting a fresh equivalent descriptor.

## State and Persistence Behavior

State is persisted in temporary LDB or REGF backing files during a test case. The recursive delete test intentionally runs before the root-info test because it verifies cleanup left no root subkeys. REGF persistence is indirectly covered through backend flush and destructor behavior, but the tests do not reopen the file after mutation.

## Dependencies and Integration Points

The file integrates registry hive APIs, winreg constants, filesystem helpers, loadparm/event torture context, and Samba security descriptor helpers. It is compiled into `torture_registry`.

## Risks and Edge Cases

The same test names run across two backends, which is useful for contract consistency, but tests do not cover large values, default value names in the hive layer, class names, deep subkey list growth, RI list support, or malformed backing stores. Security descriptor comparison checks equality but not reference-count behavior in REGF.

## Test Signals

Passing both LDB and REGF tcase variants signals that backend add/delete/list/value/security operations meet the hive contract. High-value additions would reopen mutated hives, test value resizing, add many sorted subkeys, and verify backend-specific unsupported-operation errors.

Source-read signal: reviewed complete local file (440 lines).
