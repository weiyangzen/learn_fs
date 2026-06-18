# sources/user-network-fs/impacket/tests/dcerpc/test_mimilib.py

Purpose: tests Impacket's Mimikatz RPC compatibility helpers (`mimilib`) over TCP, including Diffie-Hellman key exchange, RC4 command encryption, command execution, and unbind.

Important APIs and functions: `MimiKatzTests` binds `mimilib.MSRPC_UUID_MIMIKATZ`, uses mapper TCP, and sets a long timeout. `get_dh_public_key()` builds `MimiDiffeH`, `PUBLICKEYBLOB`, and `MIMI_PUBLICKEY`. `get_handle_key()` calls `hMimiBind`, computes the shared secret, and returns a handle plus the last 16 bytes as key material. Tests cover raw/helper `MimiBind`, raw/helper `MimiCommand`, and raw `MimiUnbind`. Authenticated subclasses add integrity and privacy variants.

Control flow: bind tests send the public key and assert zero error plus RC4 session type. Command tests encrypt `token::whoami` as UTF-16LE with RC4 using reversed key bytes, send it, assert encrypted result length, and decrypt the result locally. Unbind sends the handle from the bind handshake.

State and persistence behavior: command execution depends on a live remote Mimikatz RPC server and may inspect security-token context. The default command is read-only, but the protocol can execute sensitive commands.

Dependencies and integration points: depends on `Cryptodome.Cipher.ARC4`, `mimilib`, endpoint mapper, and a target exposing the Mimikatz RPC interface. Authn subclasses reuse the same test methods with RPC authentication levels.

Risks: highly sensitive security-tool integration. The decrypted command output is not asserted. Importing `Cryptodome` at module import time makes the whole file fail if pycryptodomex is missing. Must only run in authorized lab environments.

Test signals: validates custom protocol structures, DH public-key serialization, shared secret derivation, RC4 command/result framing, handle lifecycle, and behavior under unauthenticated/authenticated RPC levels.
