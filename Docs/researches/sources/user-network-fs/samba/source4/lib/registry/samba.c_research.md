# sources/user-network-fs/samba/source4/lib/registry/samba.c

## Purpose

`samba.c` opens Samba's local registry view by mounting named private-directory hive files under standard predefined HKEY roots. It is the source4 local-registry composition layer above the generic local registry and concrete hive backends.

## Important APIs, Types, and Functions

`reg_open_samba()` is the public entry point. `mount_samba_hive()` constructs `<private_dir>/<name>.ldb`, opens the hive with `reg_open_hive()`, falls back to `reg_open_ldb_file()` on `WERR_FILE_NOT_FOUND`, and mounts it with `reg_mount_hive()`.

## Control Flow

`reg_open_samba()` first creates an empty local registry context with `reg_open_local()`. It then attempts to mount `hklm.ldb`, `hkcr.ldb`, `hkcu.ldb`, and `hku.ldb` under `HKEY_LOCAL_MACHINE`, `HKEY_CLASSES_ROOT`, `HKEY_CURRENT_USER`, and `HKEY_USERS`. The helper returns an error on mount failure, but the caller currently does not check individual mount results.

## State and Persistence Behavior

The function can create missing LDB hive files in Samba's private directory through the fallback open path. The returned registry context is in-memory, while mounted hives persist through their LDB backend. There is no direct support here for dynamic keys, alias keys, or user-profile NTUSER.DAT loading.

## Dependencies and Integration Points

It depends on loadparm's private directory, registry local/hive mounting APIs, authentication session info, credentials, and tevent. CLI tools use `reg_common_open_local()`, Python exposes `open_samba()`, and tests can mount hives explicitly for isolated local registries.

## Risks and Edge Cases

Ignored `mount_samba_hive()` results mean `reg_open_samba()` can return success with missing predefined roots. FIXME comments document incomplete Windows semantics for HKCR merging, HKCU profile loading, HKCC aliasing, performance data, hardware, and SAM/Security aliases. Callers that assume all standard roots exist need to handle missing-key errors.

## Test Signals

Tests should check that `reg_open_samba()` mounts all intended hives when the private directory is writable, reports or tolerates missing hives consistently, and creates LDB hive files on first run. Tool smoke tests for `regtree`, `regshell`, and `regpatch` without `--remote` cover this path.

Source-read signal: reviewed complete local file (100 lines).
