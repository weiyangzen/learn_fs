# sources/user-network-fs/samba/source4/libnet/py_net.c

## Purpose

`py_net.c` implements the `samba.net` Python extension type `net.Net`, exposing selected libnet management, password, time, user, DC discovery, and DRS replication helper operations to Python.

## Important APIs, Types, and Functions

Python methods include:
- `join_member()` -> `libnet_Join_member()`.
- `change_password()` -> `libnet_ChangePassword()`.
- `set_password()` -> `libnet_SetPassword()`, with optional `force_samr_18`.
- `time()` -> `libnet_RemoteTOD()`.
- `create_user()` and `delete_user()` -> `libnet_CreateUser()`/`libnet_DeleteUser()`.
- `replicate_init()` creates `replicate_state`, initializes vampire callback state, extracts DRS auth session key, and populates forest/chunk context.
- `replicate_chunk()` validates DRS ctr/request Python types, selects schema vs normal chunk callback, maps ctr/request fields into `libnet_BecomeDC_StoreChunk`, checks extended-op return codes, and calls vampire chunk handlers.
- `replicate_decrypt()` decrypts a DRS replicated attribute in place using the DRS binding auth session key and RID.
- `finddc()` calls CLDAP DC discovery and returns a Python NDR NETLOGON response object.

The file defines `py_net_Type`, constructor `net_obj_new()`, destructor `py_net_dealloc()`, and module init that exposes join-level constants.

## Control Flow

The constructor requires credentials, accepts optional loadparm and server address, creates a talloc context and event context, initializes `libnet_context`, and stores credentials. Each method parses Python arguments, builds the corresponding C request, allocates a talloc frame/context, calls C libnet or DSDB/DRSUAPI helpers, translates NTSTATUS/WERROR/DRS extended errors into Python exceptions, and returns Python scalars/NDR objects or `None`.

Replication flow is two-step: Python calls `replicate_init()` once to obtain opaque talloc state, then feeds each `DsGetNCChanges` reply to `replicate_chunk()`. The chunk method reuses stored forest, partition, destination DSA, and session-key pointers across calls.

## State and Persistence Behavior

`net.Net` owns a persistent `libnet_context`, event context, and talloc tree for the Python object lifetime. Methods can mutate remote domain state (join, password set/change, user create/delete), read remote state (time/finddc), or mutate local DSDB state via replication chunk import. `replicate_decrypt()` mutates the provided Python DRS attribute object in place.

## Dependencies and Integration Points

The extension integrates Python C API, pytalloc, pyldb, pyparam, pycredentials, generated Python DCERPC type checks, libnet C APIs, DRSUAPI helpers, vampire callbacks, Samba finddc/CLDAP, GENSEC session keys, and Samba Python module initialization. `py_net_dckeytab.c` later injects an additional method into this same `Net` type.

## Risks and Edge Cases

Several methods create a new event context rather than accepting one from Python, noted by FIXME comments. `change_password()` frees parsed Unicode strings after the libnet call; error paths must avoid leaks. `replicate_decrypt()` has early returns after talloc stackframe allocation that can leak the frame if type checks fail. `replicate_chunk()` treats any non-`Py_None` `schema` argument as requiring a bool, so default truthiness is not accepted. Type validation is essential because it casts Python objects to generated C structs.

## Test Signals

Python-level tests should cover constructor credential validation, password operations, user create/delete, time formatting, finddc returns, DRS replicate init/chunk/decrypt paths, extended-error exception mapping, forced SAMR level 18, and bad Python type errors. Integration with Samba replication tooling is a strong end-to-end signal.
