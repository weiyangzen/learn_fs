# sources/user-network-fs/samba/source4/librpc/ndr/py_auth.c

## Purpose

`py_auth.c` patches generated Python bindings for `auth_session_info` so Python code can get and set the associated Samba credentials object.

## Important APIs And Types

`PyType_AddGetSet()` injects `PyGetSetDef` descriptors into a type dictionary. `py_auth_session_get_credentials()` extracts `struct auth_session_info` from a pytalloc object and returns `session->credentials` as a Python `samba.credentials.Credentials` NDR-like object via `py_return_ndr_struct()`. `py_auth_session_set_credentials()` converts a Python credentials object with `PyCredentials_AsCliCredentials()` and stores a talloc reference under the session.

`PY_SESSION_INFO_PATCH` is defined as `py_auth_session_info_patch` so generated binding code can invoke the patch.

## Control Flow And State

When the generated module initializes, it calls the patch macro for the generated type. Accessing `.credentials` dynamically wraps or replaces the C pointer. Setting credentials changes in-memory session state only; it does not persist credentials externally.

## Dependencies And Integration Points

It depends on Python C API, pytalloc, auth session structures, credentials Python helpers, and `pyrpc_util`.

## Risks

The getter comment notes this is not a normal IDL structure. Lifetime correctness depends on talloc references and Python wrapper ownership. The setter does not reject null conversion explicitly in this file, so converter error behavior is important.

## Test Signals

Python tests should import the auth binding, read `.credentials`, assign a `samba.credentials.Credentials` instance, and verify reference lifetime after the original Python object is dropped.
