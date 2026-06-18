# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authtis.c

SSH1 client TIS/challenge-response authentication method.

Key responsibilities:
- Sends `SSH_CMSG_AUTH_TIS`.
- Reads challenge from server.
- Prompts on `/dev/cons`.
- Sends response and waits for success/failure.

Important function:
- `authtisfn`.

Risks/quirks:
- Only works in interactive mode.
- Response buffer is fixed at 256 bytes.
