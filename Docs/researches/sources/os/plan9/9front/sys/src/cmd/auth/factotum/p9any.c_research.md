# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9any.c

Factotum protocol negotiator for Plan 9 authentication mechanisms.

Key responsibilities:
- Negotiates `p9sk1` and `dp9ik` between client and server.
- Server side advertises available `proto@domain` pairs from matching server keys.
- Client side chooses a preferred protocol/domain for which it has or can ask for a key.
- Supports version marker `v.2` and an explicit server `OK` step.
- Delegates subsequent read/write operations to the selected sub-protocol.
- Propagates sub-protocol return codes, needkey requests, confirmations, phase changes, and `AuthInfo`.

Dependencies:
- Uses factotum key lookup, attribute mutation, `p9sk1`/`dp9ik` protocol modules, and RPC logging helpers.

Notable risks:
- `p9sk1` is intentionally listed before `dp9ik` for drawterm compatibility.
- The wrapper shares selected attributes and confirmation arrays with the sub-`Fsstate`.
