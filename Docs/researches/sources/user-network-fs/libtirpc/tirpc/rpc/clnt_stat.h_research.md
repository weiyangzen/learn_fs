# sources/user-network-fs/libtirpc/tirpc/rpc/clnt_stat.h

Purpose: `clnt_stat.h` defines the client RPC status enumeration used to classify local, remote, rpcbind, TLI, async, and connection errors.

Important APIs, types, and functions: The core type is `enum clnt_stat`, including statuses such as `RPC_SUCCESS`, encode/decode/send/receive failures, timeout/interruption, version mismatch, auth errors, program/procedure unavailable, rpcbind failures, unknown host/protocol/address, async in-progress, stale handles, and connection failures.

Control flow: Client implementations return these values from `CLNT_CALL` and related helpers. Error-formatting routines and retry policies switch on this enum.

State and persistence behavior: No state is declared.

Dependencies and integration points: It is included by `auth.h` and `clnt.h`; status values are stored in `struct rpc_err` and `struct rpc_createerr`.

Risks: Numeric values are ABI-significant and cannot be reordered. Some values are legacy aliases or transport-specific, so new code must preserve old semantics. Callers often use retry/no-retry decisions based on exact enum values.

Test signals: Tests should verify status-to-string output, retry classification through `IS_UNRECOVERABLE_RPC`, and preservation of numeric ABI values.
