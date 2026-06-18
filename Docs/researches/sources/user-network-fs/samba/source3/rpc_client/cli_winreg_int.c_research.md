# sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.c research

## Purpose

`cli_winreg_int.c` provides helpers for connecting to Samba's internal WINREG server and opening registry keys. It normalizes hive/key paths, creates an internal RPC binding handle using local session information, opens the requested hive, and then opens or creates the requested key.

## Important APIs, types, and functions

The private `_split_hive_key()` normalizes a path into hive name and subkey string. The private `_winreg_int_openkey()` creates the binding and opens a hive/key for a numeric hive type. Public APIs are `dcerpc_winreg_int_openkey()` for paths containing a hive prefix and `dcerpc_winreg_int_hklm_openkey()` for paths relative to HKLM.

The implementation uses `auth_session_info`, `messaging_context`, `tsocket_address`, generated `ndr_table_winreg`, `rpcint_binding_handle()`, generated open-hive calls (`OpenHKLM`, `OpenHKCR`, `OpenHKU`, `OpenHKCU`, `OpenHKPD`), `dcerpc_winreg_OpenKey()`, and `dcerpc_winreg_CreateKey()`.

## Control flow

`_split_hive_key()` rejects NULL or empty paths, converts `/` to `\` when no backslash is present, strips trailing backslashes, splits the first path component as the hive, and returns the remainder as the subkey. `dcerpc_winreg_int_openkey()` maps hive names such as `HKLM`, `HKEY_LOCAL_MACHINE`, `HKCR`, `HKU`, `HKCU`, and `HKPD` to numeric hive constants, then delegates to `_winreg_int_openkey()`.

`_winreg_int_openkey()` creates a loopback `tsocket_address` for `127.0.0.1`, obtains an internal binding handle with the supplied session and messaging context, opens the selected hive with the requested access mask, and then either creates or opens the requested key. On create it logs whether a new or existing key was returned. On any generated NTSTATUS failure or server WERROR failure it frees the binding handle and returns the error. On success it returns the binding handle and policy handles to the caller.

## State and persistence behavior

The function returns live RPC binding and policy handles. If `create_key` is true it can create registry keys in the internal registry server. Otherwise it only opens existing keys. It allocates path pieces and handles under the caller's `mem_ctx` and writes no local files.

## Dependencies and integration points

This file integrates source3 server-side session identity, messaging, internal RPC binding creation (`rpc_server/rpc_ncacn_np.h`), generated WINREG RPC stubs, and registry constants from `include/registry.h`. Higher-level registry code can combine these open helpers with typed value helpers from `cli_winreg.c`.

## Risks and edge cases

There is a notable path-handling risk: `dcerpc_winreg_int_openkey()` computes both `hivename` and `subkey`, but delegates to `_winreg_int_openkey()` with `key` rather than `subkey`. If generated WINREG `OpenKey` expects a path relative to the opened hive, passing the full hive-prefixed path can fail or create/open the wrong path. `dcerpc_winreg_int_hklm_openkey()` intentionally passes the caller's key as HKLM-relative, so the inconsistency deserves focused testing.

`_split_hive_key()` only converts slash separators when the path contains no backslash at all; mixed separators are not normalized. It strips trailing backslashes before splitting. The loopback binding uses port 0 with an internal binding helper, so correctness depends on `rpcint_binding_handle()` interpreting the local address in the expected way. Access masks are reused for both hive and subkey open/create.

## Test signals

Tests should cover hive-only paths, hive plus subkey paths, legacy slash paths, mixed slash/backslash paths, trailing separators, unknown hives, create versus open behavior, each supported hive, insufficient access masks, session identity propagation, and specifically whether `dcerpc_winreg_int_openkey("HKLM\\Software\\...")` opens a key relative to HKLM or incorrectly includes the hive prefix.
