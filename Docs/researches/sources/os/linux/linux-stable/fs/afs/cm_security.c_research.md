# File Research: sources/os/linux/linux-stable/fs/afs/cm_security.c

This file handles security challenge processing for the AFS cache manager and, when enabled, constructs RxGK callback credentials.

Major responsibilities:
- Processes RxRPC out-of-band challenge packets queued on the AFS socket.
- Routes challenge responses by service ID and security class.
- Supports RxKAD challenge responses when `CONFIG_RXKAD` is enabled.
- Supports RxGK and YFS-RxGK challenge responses when `CONFIG_RXGK` is enabled.
- Creates a cache-manager security keyring and random callback token key for RxGK.
- Builds encrypted YFS callback appdata tokens for file servers.

Challenge routing:
- Only file-service and VL-service IDs are accepted for challenge responses.
- Unknown service/security combinations are rejected with user aborts and AFS unsupported-security abort codes.
- For YFS RxGK file-service challenges, the server is recovered from RxRPC peer appdata and per-server callback appdata is lazily created under `cm_token_lock`.

RxGK token creation:
- `afs_create_token_key()` creates a `kafs` keyring, attaches it to the RxRPC socket, finds AES128 Kerberos enctype support, generates random key material, and stores an `rxrpc_s` key.
- `afs_create_yfs_cm_token()` builds YFS appdata containing initiator and acceptor UUIDs, capabilities, callback key enctype/key, and an encrypted token container.
- Token sizing is calculated with XDR alignment helpers and Kerberos encryption buffer sizing.
- The token embeds callback key material, security level, timestamps/lifetimes, and server UUID identity, then encrypts the token body with Kerberos AEAD helpers.

OOB processing:
- `afs_process_oob_queue()` drains socket OOB messages and responds to challenge packets, freeing each OOB skb afterward.
