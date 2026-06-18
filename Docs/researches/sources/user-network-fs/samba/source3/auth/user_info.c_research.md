<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_info.c -->
# sources/user-network-fs/samba/source3/auth/user_info.c

## Purpose
Allocates and fills `auth_usersupplied_info`, the structure that carries client-supplied and mapped identity names, endpoints, service description, password material, and password-state metadata into the source3 authentication pipeline.

## APIs, Types, and Functions
The exported function is `make_user_info()`. It receives SMB-visible and mapped account/domain names, workstation, remote and optional local `tsocket_address` values, service description, LM/NT response blobs, optional interactive password hashes, optional plaintext password, and an `auth_password_state`. Local destructors `clear_samr_Password()` and `clear_string()` zero copied hash/plaintext secrets when talloc frees them.

## Control Flow, State, and Persistence
The function allocates a zeroed `struct auth_usersupplied_info`, duplicates string fields under it, copies socket addresses, deep-copies response blobs and interactive hashes, installs secret-clearing destructors, sets the password state, initializes `logon_parameters` to zero, and returns the object. Any allocation failure frees the partial object and returns `NT_STATUS_NO_MEMORY`. State is memory-only and lifetime-bound to the caller's talloc tree.

## Dependencies and Integration
Depends on `auth.h`, generated SAMR password types, Samba `DATA_BLOB` utilities, talloc, and tsocket address copying. It is the construction boundary between SMB session setup/parsing code and backend authentication modules, so it must preserve both the original client identity and the internally mapped identity.

## Risks and Test Signals
Primary risks are secret lifetime and partial allocation cleanup. LM/NT response blobs are not assigned explicit destructors here, while interactive hashes and plaintext are cleared on talloc free. Callers must pass non-NULL required strings and a valid remote address because the function treats allocation/copy failures as fatal. Test signals include allocation-failure cleanup, destructor zeroing of plaintext and `samr_Password`, correct preservation of client versus mapped names/domains, optional local-address behavior, and each password-state mode used by auth backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_info.c -->
