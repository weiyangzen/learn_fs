# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/dat.h

Shared factotum declarations, constants, data structures, and protocol table exports.

Key contents:
- Defines common protocol phases: `Notstarted`, `Broken`, `Established`.
- Defines factotum RPC return codes: failure, needkey, ok, errstr, toosmall, phase, confirm.
- Defines `Fsstate`, the per-open-file state for RPC parsing, protocol state, attributes, authinfo, and confirmations.
- Defines `Key`, `Keyinfo`, `Keyring`, `Logbuf`, and `Proto`.
- Declares globals for command flags, mount/service state, protocol table, and keyring.
- Declares shared helpers from `confirm.c`, `fs.c`, `log.c`, `rpc.c`, `util.c`, and all protocol modules.

Role:
- Acts as the internal ABI between factotum's 9P server, RPC dispatcher, keyring, GUI helpers, and authentication protocol modules.

Notable risks:
- Protocol modules depend on the exact `Fsstate` and `Proto` contracts.
