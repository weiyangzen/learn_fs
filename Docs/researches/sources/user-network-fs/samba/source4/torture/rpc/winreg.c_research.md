# sources/user-network-fs/samba/source4/torture/rpc/winreg.c

## Purpose

`winreg.c` is a broad torture suite for the Windows Remote Registry RPC interface. It tests hive opening, version reporting, key create/open/delete/flush/query/enumeration, value set/query/delete/enumeration, multiple-value query variants, security descriptor operations, volatile key semantics, well-known HKLM values, and dangerous shutdown RPCs.

## Important APIs, Types, and Functions

Constants define test keys and values under `winreg_torture_test`. Utility initializers build `lsa_StringLarge` and `winreg_String` length fields. Core wrappers include `test_CreateKey_opts()`, `test_OpenKey_opts()`, `test_CloseKey()`, `test_FlushKey()`, `test_DeleteKey_opts()`, `test_QueryInfoKey()`, `test_SetValue()`, `test_DeleteValue()`, and `test_OpenHive()`. Security helpers serialize and parse descriptors through `GetKeySecurity` and `SetKeySecurity`, then test DACL/SACL/owner/group presence, inheritance, blocked inheritance, and `SECINFO_*` masks. Value helpers cover standard types, unusual value names, extended registry types, `QueryValue`, `QueryMultipleValues`, `QueryMultipleValues2`, and `EnumValue`. `test_Open()` orchestrates per-hive coverage, and `torture_rpc_winreg()` registers HKLM, HKU, HKCR, HKCU, plus dangerous shutdown tests.

## Control Flow

`test_Open()` opens a hive through a function pointer, calls `GetVersion`, maps the hive to a base test key, optionally validates HKLM well-known `CurrentVersion` values, runs `test_key_base()` to create and delete temporary keys/values, skips currently disabled security-descriptor base tests, and optionally recurses through existing keys to a limited depth. `test_key_base()` cleans old test keys, creates nested keys, runs value and key-name tests, flushes, verifies deletion, and cleans up. Query helpers deliberately exercise invalid-parameter, missing-value, too-small-buffer, and successful retry paths. Shutdown tests initiate and then abort a system shutdown and are marked dangerous.

## State and Persistence Behavior

This suite intentionally mutates the remote registry by creating and deleting test keys and values under HKCU, HKU, HKCR, and `HKLM\SOFTWARE\Samba\winreg_torture_test`. It writes random binary data and multiple registry types, flushes keys, and may write security descriptors in helper paths, though the high-level security descriptor test is currently skipped. Volatile key and symlink key tests are skipped for Samba or globally disabled in relevant paths. If cleanup fails or a dangerous shutdown test is run, persistent registry keys or a pending shutdown can affect the target; the shutdown tests call `AbortSystemShutdown` afterward.

## Dependencies and Integration Points

The file integrates generated winreg client stubs, generated security NDR, Samba registry helpers such as `push_reg_sz`, `push_reg_multi_sz`, and `str_regtype`, SID/security descriptor helpers, common RPC torture registration, and target registry service policy. It uses `test_winreg_QueryValue()` from shared torture helpers.

## Risks and Edge Cases

The file contains several deliberately skipped or disabled paths: symlink keys, key security descriptor high-level tests, and some multiple-value cases known to crash Windows 2008 remote registry. Registry semantics vary heavily by hive, privilege, Samba version, and Windows version. Some cleanup is best effort, and there is a likely typo in `test_key_base_sd()` deleting `test_key4` twice instead of deleting `test_key2`. Dangerous shutdown tests require careful opt-in. Recursive enumeration is capped by `MAX_DEPTH` but HKCR fanout is still large, so the suite special-cases it.

## Test Signals

Passing HKLM/HKU/HKCR/HKCU tests show the remote registry endpoint can open hives, create/delete keys, round-trip values across many types and names, enumerate keys and values, query well-known values, and handle expected error paths. Passing dangerous tests show shutdown RPCs and abort behavior work, but they should only run in disposable environments.
