# sources/user-network-fs/samba/source4/lib/registry/rpc.c

## Purpose

`rpc.c` implements a remote registry backend by translating generic `struct registry_operations` calls into MS-RRP/winreg DCE/RPC requests. It lets callers use the same registry API against a local `ncalrpc:` winreg endpoint or a remote server.

## Important APIs, Types, and Functions

`struct rpc_registry_context` stores the generic context, DCE/RPC pipe, and binding handle. `struct rpc_key` stores a generic key wrapper, winreg policy handle, binding handle, cached key metadata, and last change time. Public entry point `reg_open_remote()` connects to the winreg pipe. Backend methods include `rpc_get_predefined_key()`, `rpc_open_key()`, `rpc_get_subkey_by_index()`, `rpc_get_value_by_index()`, `rpc_get_value_by_name()`, `rpc_set_value()`, `rpc_del_value()`, `rpc_add_key()`, `rpc_del_key()`, `rpc_query_key()`, and `rpc_get_info()`.

## Control Flow

`reg_open_remote()` initializes DCE/RPC, defaults a missing location to `ncalrpc:`, connects with the caller's credentials/loadparm/event context, and installs `reg_backend_rpc`. Predefined-key opens use generated `winreg_OpenHK*` calls selected from `known_hives[]`. Key opens, enumeration, queries, creates, deletes, and value operations allocate winreg request structures, fill the parent policy handle and buffers, call the `_r` RPC stubs, translate transport NTSTATUS failures, and return server-side WERROR results.

## State and Persistence Behavior

The backend itself caches `QueryInfoKey` results in `struct rpc_key` by using `num_values == -1` or `num_subkeys == -1` as an unqueried marker. Mutations are persisted by the remote registry service, not locally. Open policy handles live as long as their talloc-backed key objects; this file does not explicitly close handles.

## Dependencies and Integration Points

It depends on generated `ndr_winreg_c.h` RPC clients, DCE/RPC pipe connection helpers, Samba credentials/loadparm/tevent context, `registry.h`, and winreg constants. CLI tools call it through `reg_common_open_remote()` and Python uses it indirectly through local/remote registry APIs where exposed.

## Risks and Edge Cases

Fixed `MAX_NAMESIZE` and `MAX_VALSIZE` buffers may be too small for some remote values or names, and the value buffer is declared as one byte but passed with a large size pointer, relying on NDR allocation behavior. Cached key metadata is not invalidated after mutations. Access masks are hard-coded (`SEC_FLAG_MAXIMUM_ALLOWED` or `0x02000000`) rather than caller-specific. Missing explicit handle close can matter for long-running tools. Security descriptor, flush, load/unload, and notification operations are absent from this backend table.

## Test Signals

Coverage should include opening each predefined hive, enumerating keys/values, reading and writing normal and large values, creating and deleting keys, remote access denied cases, local `ncalrpc:` default behavior, and cache behavior after mutations. Existing registry tests mostly exercise the local backend, so RPC-specific integration tests are important.

Source-read signal: reviewed complete local file (578 lines).
