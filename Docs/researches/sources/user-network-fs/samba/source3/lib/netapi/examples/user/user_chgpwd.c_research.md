# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_chgpwd.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_chgpwd.c

Purpose: Demonstrates changing a user password with `NetUserChangePassword()`.

Important APIs/types/functions: Calls `NetUserChangePassword(hostname, username, oldpassword, newpassword)`.

Control flow: Parses hostname, username, old password, and new password, calls the API, prints context error details on failure, and releases resources.

State and persistence behavior: Mutates remote account password state.

Dependencies and integration points: Complements user add/setinfo examples and tests password-change policy behavior.

Risks: Passwords are command-line arguments and may appear in process listings/history. Server password policy errors are only printed.

Test signals: Change a disposable user's password and verify authentication with the new secret.
