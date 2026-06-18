# sources/test-tools/pynfs/nfs4.1/nfs4commoncode.py

## Purpose
`nfs4commoncode.py` dynamically generates shared client/server helper classes for NFSv4 COMPOUND processing. It provides result encoders, compound result accumulators, replay-cache-aware paired results, and per-compound state classes for both normal and callback operations.

## Important APIs, Types, And Functions
- `encode_status_by_name(name, status, *args, **kwargs)` constructs an `nfs_resop4` for an operation name and generated `NAME4res` payload.
- `encode_status(status, *args, **kwargs)` infers the operation name from the caller `op_<name>` and delegates to `encode_status_by_name`.
- `CompoundArgResults` stores result structs, their packed XDR bytes, current status, tag prefix, and computed reply size.
- `PairedResults` stores both the reply sent now and the replay-cache response, inserting `NFS4ERR_RETRY_UNCACHED_REP` when only the SEQUENCE result should be cached.
- `CompoundState` stores current/saved filehandles and stateids, current session/cache/caching flag, request metadata, credential-derived principal/connection/header size, tag, and paired results.
- Callback equivalents `cb_encode_status*`, `CBCompoundArgResults`, `CBPairedResults`, and `CBCompoundState` are created from the same template.

## Control Flow
The module defines a format string containing Python source and executes it twice: once with normal operation names/types and once with callback operation names/types. Encoders create the generated result payload, wrap it in the correct `nfs_resop4` or `nfs_cb_resop4` union, attach a synthetic `status` attribute for uniform handling, and optionally attach a tag message.

During server or callback dispatch, operations append encoded results to `env.results`. `PairedResults.append` updates the reply result array and also constructs the replay-cache array depending on whether caching is enabled and which operation index is being appended. `CompoundState` is constructed once per COMPOUND and carries mutable interim state across operation handlers.

## State And Persistence Behavior
State is per-COMPOUND and in memory. `CompoundArgResults` stores packed result bytes and base length for response-size accounting. `PairedResults` stores reply and cache views for the active COMPOUND; long-term persistence is owned by session slot caches outside this module.

## Dependencies And Integration Points
The module depends on `nfs4lib`, generated constants/types, and `sys._getframe`. It is used by `nfs4server`, `nfs4client` callback handling, and `nfs4proxy` to share encoding and environment behavior across normal and callback COMPOUND processing.

## Risks And Edge Cases
- Heavy use of `exec` and generated names means errors surface at runtime and are difficult to statically inspect.
- `encode_status` depends on caller function names beginning with `op_`.
- The result union field naming conventions are acknowledged as fragile for NFSv4.1.
- `PairedResults` has comments noting missing size checks for reply and cache limits.
- `CompoundState.get_principal` assumes credentials expose `credinfo.principal`; AUTH_SYS or malformed creds may differ.
- `set_cfh` defaults state to `nfs4lib.state00`, which can unintentionally clear current stateid when resetting current filehandle.

## Test Signals
Tests should assert generated result structures pack/unpack correctly for normal and callback operations, operation tags propagate, replay-cache arrays contain either full cached results or `RETRY_UNCACHED_REP` as appropriate, and `CompoundState` exposes principal/connection/header fields used by server handlers.
