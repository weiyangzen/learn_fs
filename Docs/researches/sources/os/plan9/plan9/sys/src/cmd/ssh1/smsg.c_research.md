# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/smsg.c

SSH1 server handshake and authentication logic.

Key responsibilities:
- Loads SSH server host key from factotum.
- Generates ephemeral server RSA key.
- Sends SSH1 public-key packet and receives encrypted session key.
- Decrypts session key using server private key and factotum host key RPC.
- Authenticates user via configured server auth methods.
- Switches process credentials with `auth_chuid`.

Important functions:
- `sshserverhandshake`: full server-side setup.
- `send_ssh_smsg_public_key`: advertises keys, ciphers, auth methods.
- `recv_ssh_cmsg_session_key`: decrypts and unmunges session key.
- `authsrvuser`: drives user/auth method loop.
- `responselogin`, `authusername`: p9cr helper path.

Risks/quirks:
- Server ephemeral key is 768 bits in `sshserve.c`.
- Host key private operation is delegated through factotum RPC.
- Uses SSH1 protocol assumptions and weak legacy algorithms.
