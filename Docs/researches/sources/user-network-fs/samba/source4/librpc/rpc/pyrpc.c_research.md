# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.c

## Purpose

`pyrpc.c` implements the `samba.dcerpc.base` Python extension module. It exposes a generic `ClientConnection`, transfer syntax helper types, bind-time feature syntax construction, and a Python wrapper type for NDR pointers.

## Important APIs, Types, and Functions

The main Python type is `dcerpc_InterfaceType` backed by `dcerpc_InterfaceObject` from `pyrpc.h`. Getters expose `server_name`, `abstract_syntax`, `transfer_syntax`, `session_key`, `user_session_key`, and mutable `request_timeout`. Methods are `request()`, `transport_encrypted()`, and `auth_info()`. Helper type constructors include `py_transfer_syntax_ndr_new()`, `py_transfer_syntax_ndr64_new()`, `py_bind_time_features_syntax_new()`, and `py_dcerpc_ndr_pointer_new()`.

## Control Flow

Module init imports `talloc.BaseObject` and `samba.dcerpc.misc.ndr_syntax_id`, sets Python type bases, readies types, and registers module objects. `ClientConnection.__new__` parses a binding string plus syntax UUID/version, rejects direct `irpc:` from the generic constructor, builds a dummy interface table, and delegates connection setup to `py_dcerpc_interface_init_helper()`. Raw `request()` copies Python bytes into a talloc blob, optionally parses an object GUID, calls `dcerpc_binding_handle_raw_call()`, and returns response bytes.

## State and Persistence Behavior

Connection state is the talloc memory context, DCE/RPC pipe, binding handle, event context, and result-exception flag stored on the Python object. Deallocation reparents the event context so it is freed last. Session keys are exposed as Python bytes but not persisted.

## Dependencies and Integration Points

Dependencies include Python C API, Samba py3 compatibility helpers, pytalloc, DCE/RPC core, credentials/GENSEC indirectly through util code, and generated NDR syntax types. Generated Python RPC modules use the base connection and method registration helpers from `pyrpc_util.c`.

## Risks and Test Signals

Risks include Python reference-count mistakes, static dummy interface table reuse, raw request object GUID validation, lifetime ordering between pipe and event context, and exposing sensitive session keys. Test signals include constructing `ClientConnection` with string and tuple syntax IDs, raw request success/failure, timeout get/set, session key access failure/success, module import, and pointer wrapper get/set reference behavior.
