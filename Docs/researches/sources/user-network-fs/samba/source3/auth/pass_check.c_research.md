# sources/user-network-fs/samba/source3/auth/pass_check.c

## Purpose
This file checks plaintext Unix passwords against PAM when enabled or against system crypt-style password stores otherwise. Encrypted SMB password verification is handled elsewhere.

## Important APIs, Types, and Functions
The public API is `pass_check`. Internal `password_check` dispatches to `smb_pam_passcheck` or platform crypt functions. In non-PAM builds, static helpers maintain global copies of the current salt and encrypted password.

## Control Flow
`pass_check` rejects null passwords according to policy, short-circuits into PAM for PAM builds, otherwise loads the password hash from `passwd`, shadow, adjunct, IA, or Ultrix sources, allows empty system hashes only when null passwords are enabled, and calls `password_check`. If the initial check fails with `WRONG_PASSWORD` and `run_cracker` is true, all-uppercase passwords may be retried in lowercase unless they are mixed case.

## State and Persistence
In non-PAM builds, `ths_salt` and `ths_crypted` are static process-global buffers updated for each call. No persistent storage is written. PAM builds delegate all state to `pampass.c` and PAM modules.

## Dependencies and Integration Points
Dependencies include system passwd/shadow APIs, `crypt`/`bigcrypt`/`crypt16` variants depending on platform, PAM password checking, loadparm null-password policy, and string case helpers. It is called by `auth_unix.c`.

## Risks and Test Signals
Risks include process-global salt/hash buffers in threaded contexts, platform-specific shadow access requiring root, weak lowercase retry behavior, null-password policy mistakes, and compile-time code paths that may be rarely exercised. Tests should cover PAM and non-PAM builds, missing users, wrong passwords, null passwords, uppercase retry behavior, shadow hash retrieval, and non-password PAM failures returning without retries.
