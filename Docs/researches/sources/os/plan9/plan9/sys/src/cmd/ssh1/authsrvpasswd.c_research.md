# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvpasswd.c

SSH1 server password authentication handler.

Key responsibilities:
- Extracts password string from client message.
- Calls `auth_userpasswd` for the selected connection user.
- Exports `Authsrv authsrvpassword`.

Important details:
- First expected message is `SSH_CMSG_AUTH_PASSWORD`.
- Frees the message after extracting password pointer.

Risks/quirks:
- Relies on `getstring` returning storage valid through auth call before message free implications.
