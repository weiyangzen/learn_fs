# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authpasswd.c

SSH1 client password authentication method.

Key responsibilities:
- Retrieves a password from factotum/auth helper using `auth_getuserpasswd`.
- Sends `SSH_CMSG_AUTH_PASSWORD`.
- Waits for success/failure.

Important function:
- `authpasswordfn`: full implementation.

Notable details:
- Interactive mode allows `auth_getkey`; noninteractive mode only uses available credentials.
- Exports `Auth authpassword`.

Risks/quirks:
- Password is passed in plaintext inside the already-encrypted SSH session.
