# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_rpc.c

This file implements the low-level factotum RPC client.

Key behavior:
- `auth_allocrpc` allocates an `AuthRpc` bound to an fd.
- `auth_freerpc` closes and releases it.
- `auth_rpc` sends `verb[ data]` requests and reads/classifies replies.
- `classify` maps reply text to `ARok`, `ARdone`, `ARerror`, `ARneedkey`, `ARbadkey`, `ARtoosmall`, and `ARphase`.

Important details:
- RPC data is stored in `rpc->arg` with `rpc->narg`.
- Reply classification is string-prefix based and preserves returned payload after the status word.
