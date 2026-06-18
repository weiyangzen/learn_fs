# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rpc.c

Implements `/mnt/factotum/rpc` request parsing and `/mnt/factotum/ctl` key-management writes. RPCs are paired write/read cycles with verbs `start`, `read`, `write`, `authinfo`, and `attr`.

`rpcwrite` records a pending verb and binary argument. `rpcread` executes it: `start` parses attrs and initializes a protocol; `read` and `write` dispatch to the active protocol state machine; `authinfo` serializes `AuthInfo` with a generated capability; `attr` returns current attrs.

Return handling maps internal `Rpc*` codes into textual responses or queues confirmation/needkey requests. `ctlwrite` supports `key`, `delkey`, and `debug`, splits public/private attrs, handles multi-protocol key addition, and validates private-field deletion patterns.
