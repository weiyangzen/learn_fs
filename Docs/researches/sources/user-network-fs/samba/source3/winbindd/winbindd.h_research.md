# sources/user-network-fs/samba/source3/winbindd/winbindd.h

Purpose: central winbindd header defining daemon/client/domain state, backend method tables, idmap config structures, enumeration cursors, cached credential structures, constants, and generated prototypes.

Important APIs and types: `struct winbindd_cli_state`; `struct winbindd_domain_ref` and `_winbindd_domain_ref_set/get` macros; `struct getpwent_state`; `struct getgrent_state`; `struct winbindd_cm_conn`; `struct winbindd_child`; `struct winbindd_domain`; `struct wb_parent_idmap_config(_dom)`; `struct wb_acct_info`; `struct winbindd_methods`; `struct winbindd_idmap_methods`; trusted-domain and credential cache structs; constants `WB_REPLACE_CHAR`, `WINBINDD_ESTABLISH_LOOP`, `WINBINDD_RESCAN_FREQ`, `DOM_SEQUENCE_NONE`.

Control flow role: the header itself has no runtime flow, but its structures define the state machines used by async request handlers, domain iteration, child RPC, ADS/MSRPC backend selection, idmap setup, and NSS enumeration.

State and persistence: declares in-memory state for client sockets, per-request memory, output queues, domain trust metadata, connection handles, children, caches, ccache entries, and memory credentials. Some structs mirror persistent or semi-persistent stores such as trusted-domain cache, idmap configuration, Kerberos ccaches, and domain sequence numbers.

Dependencies and integration points: includes nsswitch protocol structs, libwbclient, generated RPC headers, tevent NTSTATUS helpers, optional nscd and mmap headers, and generated `winbindd_proto.h`. It is included by most source3/winbindd files and anchors backend polymorphism via `winbindd_methods`.

Risks: structure changes are ABI-sensitive inside the daemon and can affect many files. Domain refs are designed to detect stale domain pointers; bypassing them risks use-after-free. Method-table contracts must be respected by ADS/MSRPC/cache layers. Client state owns per-request memory and enumeration cursors, so lifetime mistakes can leak or corrupt NSS enumeration.

Test signals: compile coverage is essential after any struct or method signature change. Runtime tests should cover stale domain ref detection, backend method substitution, getpwent/getgrent cursor lifetime across client requests, and privileged/nonprivileged client state handling.
