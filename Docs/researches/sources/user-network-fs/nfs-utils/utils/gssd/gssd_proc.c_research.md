<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd_proc.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gssd_proc.c

## Purpose
This file handles actual gssd upcalls. It parses kernel requests, selects user or machine Kerberos credentials, creates RPCSEC_GSS contexts with servers, serializes contexts for the kernel, and writes success or error downcalls.

## APIs And Control Flow
`handle_krb5_upcall` reads a uid from the legacy pipe; `handle_gssd_upcall` parses text fields such as `mech=`, `uid=`, `target=`, `service=`, `srchost=`, and `enctypes=`, then starts a worker. `start_upcall_thread` creates a pthread and records it in the watchdog list. `process_krb5_upcall` chooses user creds via `krb5_not_machine_creds` or machine creds via `krb5_use_machine_creds`, creates an authenticated RPC client, extracts private authgss context data, inquires lifetime/acceptor name, serializes the context with `serialize_context_for_kernel`, and calls `do_downcall`. Error paths call `do_error_downcall`. `create_auth_rpc_client` builds the RPC client, sets allowable enctypes when supported, populates ports, and handles bad-integrity retries.

## State, Dependencies, And Integration
State includes global kernel enctype arrays, active thread tracking, client refs, and authgss private data. Dependencies are libtirpc/rpcsec_gss, GSSAPI, Kerberos utility functions, nfs RPC helpers, pthread cancellation, and kernel pipe downcall formats.

## Risks And Test Signals
Risks include thread cancellation around library calls, direct syscall identity changes, shared enctype globals updated by upcalls, parsing fixed-size text buffers, partial pipe writes, DNS/rpcbind dependence, and service-ticket repair heuristics. Test malformed upcalls, user and machine credential paths, gssproxy/allowable enctype intersections, timeout cancellation, bad integrity retry, NFSv4 port defaults, and kernel downcall binary layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd_proc.c -->
