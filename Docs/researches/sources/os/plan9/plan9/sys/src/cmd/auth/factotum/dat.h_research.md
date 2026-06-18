# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/dat.h

Shared factotum internal declarations and protocol interfaces.

Key points:
- Defines RPC phases, return codes, and core structs: `Fsstate`, `Key`, `Keyinfo`, `Keyring`, `Logbuf`, and `Proto`.
- `Fsstate` tracks per-RPC transient buffers, persistent auth attributes, phase state, protocol private state, pending confirmations, and `AuthInfo`.
- `Key` stores public/private attributes, protocol pointer, parsed protocol-private key data, and success count.
- Declares functions across confirm, filesystem, log, RPC, secstore, and utility modules.
- Declares available protocol implementations including APOP, CRAM, p9sk, CHAP, MSCHAP, p9cr, VNC, pass, RSA, WEP, and HTTP digest.

Dependencies:
- Includes Plan 9 auth, authsrv, libsec, mp, String, thread, fcall, and 9p headers.

Notable behavior:
- Uses an incomplete `State` type for protocol-private state.
