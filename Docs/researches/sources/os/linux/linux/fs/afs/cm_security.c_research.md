# File Research: sources/os/linux/linux/fs/afs/cm_security.c

Purpose: handles RxRPC out-of-band security challenges for AFS/VL/YFS services and, when RxGK is enabled, creates cache-manager callback tokens.

Key interfaces:
- `afs_process_oob_queue()`.
- `afs_create_token_key()` under `CONFIG_RXGK`.

Implementation notes:
- OOB worker dequeues RxRPC challenge messages and responds based on service ID and security index.
- Accepts challenges for FS, VL, YFS FS, and YFS VL services; unknown services are rejected with `afs_abort_unsupported_sec_class`.
- Supports RxKAD challenge response when configured.
- Supports RxGK and YFS-RxGK; YFS callback appdata is lazily generated per server under `cm_token_lock`.
- RxGK token key creation builds a `kafs` keyring, attaches it to the socket, chooses AES128 CTS HMAC SHA1, generates a random callback key, and creates an `rxrpc_s` key.
- YFS CM token construction builds XDR appdata containing initiator/server UUIDs, capabilities, callback key, and encrypted token container.

Dependencies:
- RxRPC challenge APIs, Linux keyrings, Kerberos crypto helpers, random bytes, YFS protocol constants.

Edge cases:
- Missing RxGK key returns `-ENOKEY`; unsupported enctype returns `-ENOPKG`.
- Appdata size is checked after construction and logged if mismatched.
