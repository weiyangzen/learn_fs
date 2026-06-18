# sources/user-network-fs/samba/source3/rpc_client/cli_winreg.h research

## Purpose

`cli_winreg.h` declares typed source3 helper APIs for WINREG RPC operations. It lets callers query and set registry values using Samba-native C types instead of manually marshalling WINREG byte buffers and generated NDR structures.

## Important APIs, types, and functions

The header declares typed query functions for DWORD, binary, multi-string, string, and security descriptor values: `dcerpc_winreg_query_dword()`, `dcerpc_winreg_query_binary()`, `dcerpc_winreg_query_multi_sz()`, `dcerpc_winreg_query_sz()`, and `dcerpc_winreg_query_sd()`.

It declares typed setters `dcerpc_winreg_set_dword()`, `dcerpc_winreg_set_sz()`, `dcerpc_winreg_set_expand_sz()`, `dcerpc_winreg_set_multi_sz()`, `dcerpc_winreg_set_binary()`, and `dcerpc_winreg_set_sd()`. It also declares `dcerpc_winreg_add_multi_sz()`, `dcerpc_winreg_enum_keys()`, `dcerpc_winreg_enumvals()`, and `dcerpc_winreg_delete_subkeys_recursive()`.

## Control flow and contracts

All APIs require an existing WINREG `dcerpc_binding_handle` and an already-opened `policy_handle` for the relevant key or hive. The functions return transport/call NTSTATUS and write server-side registry status to `WERROR *pwerr`. Query outputs and enumeration arrays are talloc-owned under `mem_ctx`.

The header documents value-type expectations, but callers must still check both NTSTATUS and WERROR. Enumeration returns arrays whose shape depends on server-reported counts. Recursive deletion expects a hive handle plus a key path relative to that hive.

## State and persistence behavior

The header exposes mutating APIs that alter registry values and keys on the target server. It has no local state. Output memory ownership is through the supplied talloc context.

## Dependencies and integration points

Consumers include registry tools, print/registry configuration code, and internal WINREG open helpers. The declarations integrate generated WINREG types, security descriptors, and Samba `DATA_BLOB` with higher-level registry workflows.

## Risks and test signals

Misuse risks include ignoring `pwerr`, passing a policy handle opened with insufficient access rights, using setters with data not encoded as expected for Windows registry semantics, and recursively deleting unintended keys. Tests should compile-check generated type compatibility and behaviorally validate dual-status handling, ownership of returned arrays/blobs, and destructive operation safeguards at caller layers.
