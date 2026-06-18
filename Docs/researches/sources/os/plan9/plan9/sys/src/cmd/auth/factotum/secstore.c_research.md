# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/secstore.c

Embeds a reduced secstore client inside factotum for boot-time key retrieval. `havesecstore` probes the secstore server for the current `owner`, and `secstorefetch` authenticates, handles optional STA, fetches the `factotum` file, decrypts it, and feeds each line to `ctlwrite`.

This file duplicates enough of secstore’s secure connection and PAK password-authenticated key exchange to operate without the full secstore command. `SConn` records are framed with SSL-style two-byte lengths, can switch to RC4/SHA1 authenticated encryption, and use sequence-numbered SHA1 integrity checks.

Fetched secstore files are AES-CBC decrypted using a key derived from the secstore password and authenticated by a trailing `XXXXXXXXXXXXXXXX` sentinel. The decrypted file is expected to contain factotum `key ...` control lines.
