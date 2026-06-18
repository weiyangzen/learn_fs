# sources/user-network-fs/samba/source3/auth/auth_unix.c

## Purpose
This file implements the `unix` auth backend for plaintext username/password checks against the host password database or PAM. It is used when encrypted SMB passwords are disabled or plaintext Unix auth is explicitly part of the method chain.

## Important APIs, Types, and Functions
The main checker is `check_unix_security`; `auth_init_unix` creates an `auth_methods` record and `auth_unix_init` registers it.

## Control Flow
The checker extracts an IP remote host string from the supplied tsocket address, becomes root, looks up the mapped account with `Get_Pwnam_alloc`, calls `pass_check` with the plaintext password and remote host, then drops root. On success it converts the passwd record into `auth_serversupplied_info` using `make_server_info_pw`; if the passwd record is missing it returns `NO_SUCH_USER`.

## State and Persistence
No file-local persistent state is kept. It reads OS account/shadow/PAM state through `pass_check` and returns server info with Unix UID/GID from the passwd record.

## Dependencies and Integration Points
Dependencies include system passwd APIs, PAM or crypt-based password checking, tsocket remote addresses, privilege elevation helpers, and server-info conversion. It integrates with the auth chain selected for standalone plaintext mode.

## Risks and Test Signals
Risks include plaintext-only semantics, character-set assumptions documented in the code, incorrect root privilege boundaries, and inconsistency between the passwd record used for checking and server-info creation. Tests should cover valid/invalid plaintext logons, null password policy, PAM-enabled and non-PAM builds, missing users, and remote-host propagation to PAM.
