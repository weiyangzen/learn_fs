<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcbind.h -->
# sources/user-network-fs/rpcbind/src/rpcbind.h

Purpose: Shared rpcbind header defining common request structures, daemon globals, service entry points, security hooks, warm-start hooks, and utility APIs used across the rpcbind daemon, service dispatchers, compatibility code, and helper modules.

Important APIs, types, and functions: Defines `encap_parms` and `r_rmtcall_args` for remote-call forwarding, including target program/version/procedure, local reply version, target universal address, and opaque argument payload. Declares global daemon flags (`debugging`, `doabort`, `verboselog`, `insecure`, `oldstyle_local`), the RPCB v3/v4 registration list `list_rbl`, and optional PORTMAP globals. Function groups include bind tracking (`add_bndlist`, `is_bound`), address merging (`mergeaddr`, `addrmerge`), RPCB stats, v3/v4 services, shared RPC procedures, event loop, abort/reap/log toggles, access checks, warm-start persistence, and network initialization.

Control flow and integration: The header links `rpcbind.c` startup with `rpcb_svc_com.c` request implementations, `security.c` access policy, `util.c` address selection, `warmstart.c` state persistence, version-specific RPC service files, and optional portmap service support. `RPCB_ALLVERS` and `RPCB_ONEVERS` define the semantic selector for GETADDR-style version matching.

State and persistence: The header exposes global mutable state rather than encapsulating it. Persistence-related declarations are limited to warm-start directory creation plus read/write functions; the actual serialized format and file paths live in `warmstart.c`.

Dependencies: Includes `<rpc/rpcb_prot.h>` and optionally `<rpc/pmap_prot.h>`, so consumers need libtirpc/SunRPC headers and the build-time feature macros that match the daemon configuration.

Risks: Wide global declarations make ordering and ownership implicit. Several functions return static storage or allocated strings depending on implementation, so callers must follow module-specific conventions. The conditional `PORTMAP` declarations change ABI expectations across builds.

Test signals: Header-level validation is compile/link coverage across feature combinations. Important tests are full daemon builds with and without `PORTMAP`, `WARMSTART`, `RMTCALLS`, and IPv6, because this header is the contract connecting those modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcbind.h -->
