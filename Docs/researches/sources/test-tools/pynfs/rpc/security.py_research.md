# sources/test-tools/pynfs/rpc/security.py

Purpose: authentication/security abstraction for ONC RPC flavors `AUTH_NONE`, `AUTH_SYS`, and optionally `RPCSEC_GSS`, including credential packing, verifier generation/checking, context establishment, sequence-window replay protection, and integrity/privacy wrapping.

Important APIs/types/functions: `SecError`, `CredInfo`, `AuthNone`, `AuthSys`, `GSSContext`, `AuthGss`, `supported`, `klass`, `instances`, and `instance`.

Control flow: callers create `CredInfo` from an auth instance. Client-side `make_cred`, `make_call_verf`, and `secure_data` prepare RPC calls. Server-side `check_auth` validates flavor-specific credentials/verifiers and returns a credential context or raises `rpclib` flow-control replies. `AuthGss.init_cred` performs an RPCSEC_GSS init/continue token exchange over a supplied call function, while `handle_gss_init` accepts server-side tokens and returns `rpc_gss_init_res`.

State and persistence behavior: `AuthNone` is stateless; `AuthSys` carries per-call authsys parameters. `AuthGss` stores context handles mapped to `GSSContext`, and each context tracks client seqid, highest server seqid, and a replay-window bitmask. No durable state is written.

Dependencies/integration: depends on generated RPC/GSS XDR modules, optional `gssapi`, `rpclib`, `xdrlib3` or stdlib `xdrlib`, threading locks, and logging. If `gssapi` import fails, RPCSEC_GSS is omitted from `supported`.

Risks and test signals: several comments mark STUB/BUG areas, including service authorization, qop handling, context locking, overflow, and incomplete verifier checks during GSS init. `handle_gss_init` uses `major` after an exception path where it may be undefined. Replay-window logic silently drops repeats/out-of-window requests via `RPCDrop`, which can appear as timeouts at callers.
