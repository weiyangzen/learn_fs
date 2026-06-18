# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cmsg.c

SSH1 client handshake, key verification, and pty request logic.

Key responsibilities:
- Reads server SSH1 identification string.
- Receives server public key packet.
- Checks host key against system and user keyrings.
- Chooses cipher, generates session key, computes session id, and sends encrypted session key.
- Authenticates user using configured auth methods.
- Requests pty and sends window-size changes.

Important functions:
- `sshclienthandshake`: full client protocol setup.
- `checkkey`: host key trust-on-first-use/system keyring enforcement.
- `send_ssh_cmsg_session_key`: double-RSA-encrypts SSH1 session key.
- `authuser`: tries supported auth methods in order.
- `requestpty`, `readgeom`, `sendwindowsize`.

Risks/quirks:
- SSH1 requires server and host RSA keys to differ by at least 128 bits.
- Interactive key mismatch prompts can allow continue/replace.
- Session key is generated with `fastrand`.
