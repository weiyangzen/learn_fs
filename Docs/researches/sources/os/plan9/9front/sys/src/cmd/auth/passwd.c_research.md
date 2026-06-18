# File Research: sources/os/plan9/9front/sys/src/cmd/auth/passwd.c

Password-change client for Plan 9 auth server accounts.

Key responsibilities:
- Authenticates the old password against the auth server.
- Defaults to `dp9ik` PAK flow, with `-1` selecting legacy non-PAK path.
- Supports `user@domain` target syntax.
- Prompts whether to change Plan 9 password and/or Inferno/POP secret.
- Sends `Passwordreq` encrypted/packed with the authenticated ticket.
- Retries new password/secret prompts if the server refuses.

Dependencies:
- Uses `authdial`, authsrv ticket/password request functions, `getpass`, `answer`, PAK hashing, and shared hardening via `private`.

Notable risks:
- Old password is retained in the request structure for the password-change protocol.
