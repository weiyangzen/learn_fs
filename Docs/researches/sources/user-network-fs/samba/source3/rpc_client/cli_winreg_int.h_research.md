# sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.h research

## Purpose

`cli_winreg_int.h` declares internal WINREG client helpers used to connect to Samba's local/internal WINREG RPC server and open registry keys. It is narrower than `cli_winreg.h`: it only covers binding and key-open setup, not typed value query/set operations.

## Important APIs, types, and functions

The header forward-declares `struct auth_session_info` and `struct dcerpc_binding_handle`, then declares `dcerpc_winreg_int_openkey()` and `dcerpc_winreg_int_hklm_openkey()`. Both return NTSTATUS and output a binding handle, hive policy handle, key policy handle, and server-side WERROR.

`dcerpc_winreg_int_openkey()` accepts a key path that must begin with a hive name such as HKLM. `dcerpc_winreg_int_hklm_openkey()` accepts a key path intended to be opened under HKEY_LOCAL_MACHINE.

## Control flow and contracts

Callers supply a talloc context, session info, messaging context, requested key, `create_key` flag, and access mask. On success they receive an internal WINREG binding handle and two policy handles. If `create_key` is true, the implementation may create the subkey path if absent. Callers should check both NTSTATUS and `pwerr`.

## State and persistence behavior

The functions can mutate registry state by creating keys. Returned handles keep local RPC resources alive until closed/freed by the caller. The header does not define persistent local state.

## Dependencies and integration points

These declarations are used by server-side or local management code that needs registry access under a specific authenticated session. The resulting binding handle can be passed to typed helpers from `cli_winreg.c`.

## Risks and test signals

Risks include passing a key path in the wrong form, ignoring `pwerr`, leaking policy handles, or creating keys unintentionally. Tests should validate both full-hive and HKLM-relative APIs, success and failure ownership, and compatibility with the typed WINREG helpers after the key is opened.
