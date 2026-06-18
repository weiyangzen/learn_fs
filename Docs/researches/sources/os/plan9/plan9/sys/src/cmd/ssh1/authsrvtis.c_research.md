# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvtis.c

SSH1 server TIS/challenge-response authentication handler.

Key responsibilities:
- Starts Plan 9 `p9cr` challenge through auth server.
- Sends SSH TIS challenge string to client.
- Receives `SSH_CMSG_AUTH_TIS_RESPONSE`.
- Validates response with `auth_response`.

Important function:
- `authsrvtisfn`.

Notable details:
- If client switches auth protocols instead of responding, message is pushed back with `unrecvmsg`.
- Logs auth challenge failures.

Risks/quirks:
- Challenge string format is user-facing and includes `Challenge:`/`Response:`.
