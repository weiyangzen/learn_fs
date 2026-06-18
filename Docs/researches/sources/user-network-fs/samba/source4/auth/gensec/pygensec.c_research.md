<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/pygensec.c -->
# sources/user-network-fs/samba/source4/auth/gensec/pygensec.c

Purpose: Python extension module `samba/gensec.so` exposing Samba's Generic Security interface as `gensec.Security`. It lets Python tests and tools create client/server GENSEC contexts, choose mechanisms, perform update dances, wrap/unwrap packets, sign/check DCE/RPC packets, and inspect session information.

Important APIs and types: class constructors are `Security.start_client(settings=None)` and `Security.start_server(settings=None, auth_context=None)`. `settings_from_object()` expects a Python dict containing `target_hostname` and `lp_ctx`. Methods wrap `gensec_set_target_hostname`, `gensec_set_target_service`, `gensec_set_credentials`, `gensec_start_mech_by_name`, `gensec_start_mech_by_sasl_name`, `gensec_start_mech_by_authtype`, `gensec_update`, `gensec_wrap`, `gensec_unwrap`, `gensec_sign_packet`, `gensec_check_packet`, `gensec_session_info`, and `gensec_session_key`. Module constants mirror `GENSEC_FEATURE_*`.

Control flow: constructors allocate a talloc stackframe, initialize settings or global loadparm defaults, call `gensec_init()`, then `gensec_client_start()` or `gensec_server_start()` and transfer ownership to a pytalloc Python object. `update()` copies the input bytes because lower GENSEC code may mutate its input, returns `(finished, blob_out)`, and treats `NT_STATUS_MORE_PROCESSING_REQUIRED` as a successful nonterminal result. Wrap/unwrap and packet signing allocate a temporary talloc context, call the C API, return Python bytes, and translate NTSTATUS failures into Python exceptions.

State and persistence: Python `Security` instances own a `struct gensec_security` through pytalloc. Target names, credentials, selected mechanism, negotiated features, session keys, and security context state are stored in that native object. Temporary DATA_BLOBs are freed before returning; returned Python bytes own their copies.

Dependencies and integration: depends on Python C API, pytalloc, pyparam, pycredentials, pyrpc_util, pyerrors, tevent, and GENSEC internals. It is built as `samba/gensec.so` by the local wscript and is a primary test and scripting surface for authentication mechanisms.

Risks and test signals: `settings_from_object()` sets specific `ValueError`s but callers in constructors turn a NULL settings result into `PyErr_NoMemory()`, which can mask configuration errors. Packet functions parse `z#` buffers and require correct Python 3 size macro setup. Tests should cover missing settings keys, default loadparm creation, auth context type checking, mechanism selection failures, multi-step updates, sign/seal feature negotiation, and bytes-copy behavior for mutable GENSEC backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/pygensec.c -->
