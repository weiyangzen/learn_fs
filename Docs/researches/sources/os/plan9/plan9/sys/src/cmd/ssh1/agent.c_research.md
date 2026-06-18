# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/agent.c

SSH1 agent forwarding implementation backed by Plan 9 factotum.

Key responsibilities:
- Requests agent forwarding from the SSH server.
- Maintains up to 16 forwarded agent channels.
- Reassembles agent protocol messages from SSH channel data.
- Lists RSA keys from `/mnt/factotum/ctl`.
- Answers RSA challenge requests by asking factotum to decrypt.

Important functions:
- `startagent`: sends `SSH_CMSG_AGENT_REQUEST_FORWARDING`.
- `handleagentmsg`: collects length-prefixed agent messages.
- `handlefullmsg`: handles identity listing and RSA challenge response.
- `dorsa`: factotum RSA decrypt path.
- `handleagentopen`, `handleagentieof`, `handleagentoclose`: channel lifecycle.

Security/data flow:
- Private keys remain in factotum; code sends challenges to factotum and returns MD5(challenge||session-id).
- Add/remove identity operations deliberately fail.

Risks/quirks:
- Static channel array limits concurrent forwarded channels.
- Agent message length controls allocation through `erealloc`.
- Some channel close paths are asymmetric and compatibility-oriented.
