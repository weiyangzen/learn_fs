# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh.h

Shared header for Plan 9 SSH1 client/server tools.

Key responsibilities:
- Defines SSH1 packet type numbers, protocol flags, agent packet types, cipher IDs, auth method IDs, and constants.
- Defines core structs: `Auth`, `Authsrv`, `Cipher`, opaque `CipherState`, `Conn`, and `Msg`.
- Declares all shared APIs across message, handshake, auth, cipher, keyring, agent, and utility modules.

Important structures:
- `Conn`: carries fds, cipher state, cookies/session ids/session key, keys, auth/cipher preference lists, user/host aliases, server private keys, and unget message.
- `Msg`: packet buffer with read/write pointers and optional link for sshnet queues.

Risks/quirks:
- SSH1 protocol is inherently legacy and pre-MAC.
- Header exposes many global modules and extern variables.
