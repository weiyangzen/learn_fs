# sources/user-network-fs/samba/source3/rpc_client/cli_winreg.c research

## Purpose

`cli_winreg.c` provides typed helper functions over generated WINREG RPC calls. It queries, sets, enumerates, and recursively deletes registry values/keys while converting between Samba-native data representations and WINREG wire formats such as `REG_DWORD`, `REG_BINARY`, `REG_SZ`, `REG_EXPAND_SZ`, `REG_MULTI_SZ`, and security descriptors.

## Important APIs, types, and functions

Typed query APIs are `dcerpc_winreg_query_dword()`, `dcerpc_winreg_query_binary()`, `dcerpc_winreg_query_multi_sz()`, `dcerpc_winreg_query_sz()`, and `dcerpc_winreg_query_sd()`. Set APIs are `dcerpc_winreg_set_dword()`, `dcerpc_winreg_set_sz()`, `dcerpc_winreg_set_expand_sz()`, `dcerpc_winreg_set_multi_sz()`, `dcerpc_winreg_set_binary()`, and `dcerpc_winreg_set_sd()`. Mutation/enumeration helpers are `dcerpc_winreg_add_multi_sz()`, `dcerpc_winreg_enum_keys()`, `dcerpc_winreg_enumvals()`, and `dcerpc_winreg_delete_subkeys_recursive()`.

The file uses generated `winreg_String`, `winreg_StringBuf`, `winreg_ValNameBuf`, `winreg_Type`, `policy_handle`, `NTTIME`, and generated WINREG RPC calls. It also uses registry utility marshalling functions `pull_reg_multi_sz()`, `pull_reg_sz()`, `push_reg_sz()`, and `push_reg_multi_sz()`, plus NDR security descriptor push/pull functions.

## Control flow

Typed query helpers follow a two-call flow. They first call `dcerpc_winreg_QueryValue()` with no data buffer to obtain type and size. They verify the returned type, allocate a zeroed blob of the reported size, call `QueryValue()` again with a buffer, then decode the result into a typed output. DWORD queries require `REG_DWORD` and exactly four bytes. String and multi-string queries use registry utility pull helpers. Security descriptor queries call the binary query helper and then NDR-decode a `security_descriptor`.

Set helpers marshal typed input into a `DATA_BLOB` and call `dcerpc_winreg_SetValue()` with the matching registry type. `dcerpc_winreg_set_sd()` NDR-encodes the descriptor and delegates to binary set. `dcerpc_winreg_add_multi_sz()` reads the existing multi-string list, appends one pointer plus a NULL terminator, and writes it back.

`dcerpc_winreg_enum_keys()` calls `QueryInfoKey()` to obtain subkey counts and maximum lengths, allocates an array, then loops over `EnumKey()`. It treats `WERR_NO_MORE_ITEMS` as successful termination. `dcerpc_winreg_enumvals()` similarly calls `QueryInfoKey()` for value counts and maximum buffer sizes, loops over `EnumValue()`, and returns parallel arrays of names, types, and `DATA_BLOB`s. `dcerpc_winreg_delete_subkeys_recursive()` opens a key, enumerates its subkeys, recursively deletes children, closes the opened key handle, and deletes the key from its hive handle.

## State and persistence behavior

The file maintains no local persistent state. It directly reads and mutates the remote or internal registry visible through the supplied binding handle and policy handles. Local allocations are under `mem_ctx` or stackframe temporary contexts. Recursive deletion changes server registry state and should be treated as destructive.

## Dependencies and integration points

The helpers sit above generated `ndr_winreg_c` stubs and below registry management callers. They integrate with security descriptor NDR helpers, registry string/multi-string utilities, Samba status conventions (`NTSTATUS` plus output `WERROR`), and policy handles opened elsewhere, including by `cli_winreg_int.c`.

## Risks and edge cases

Type-specific query helpers return `NT_STATUS_OBJECT_TYPE_MISMATCH` when server type differs, while server-side `WERROR` remains in `pwerr`; callers need to check both. `dcerpc_winreg_set_dword()` allocates a blob and writes to it without explicitly checking allocation before `SIVAL()`, unlike several other helpers. `dcerpc_winreg_add_multi_sz()` does not special-case a failed query before iterating over `a`; a failed query can still lead to appending to a NULL list and overwriting the value depending on `pwerr` and caller expectations.

Enumeration relies on maximum lengths reported by `QueryInfoKey()`; changing registry contents during enumeration can produce truncated data, early `NO_MORE_ITEMS`, or mismatched final counts. `dcerpc_winreg_enum_keys()` sets `*pnum_subkeys` to the original queried count even if enumeration breaks early on `NO_MORE_ITEMS`. Recursive deletion uses caller `mem_ctx` for recursive path allocations and can grow memory with deep trees.

## Test signals

Tests should cover each registry type query/set, type mismatch handling, zero-length binary/string values, security descriptor round trip, multi-string append with existing and missing values, enumeration of empty and populated keys, changing values during enumeration, recursive deletion with nested keys, handle close behavior, and dual-status propagation where NTSTATUS succeeds but WERROR fails.
