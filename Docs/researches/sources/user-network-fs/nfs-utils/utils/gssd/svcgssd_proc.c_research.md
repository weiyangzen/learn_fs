# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_proc.c

Purpose: this file handles server-side RPCSEC_GSS init upcalls from the kernel, accepts GSS security contexts, maps client principals to local credentials, serializes completed contexts, and writes init/context responses back to kernel procfs channels.

Important APIs and types: `handle_nullreq()` is the external entrypoint. `do_svc_downcall()` writes context cache data to `/proc/net/rpc/auth.rpcsec.context/channel`. `send_response()` writes accept status and output token data to `/proc/net/rpc/auth.rpcsec.init/channel`. `get_ids()` converts a GSS name to uid/gid via `nfs4_gss_princ_to_ids()`, and `add_supplementary_groups()` fills auxiliary groups. `struct svc_cred` stores uid, gid, and up to `NGROUPS`.

Control flow: the handler qword-decodes input handle/token. A non-empty handle restores an in-progress `gss_ctx_id_t`; otherwise a fresh accept starts. It applies Kerberos enctype limits, calls `gss_accept_sec_context()`, returns continuation state when needed, or on completion maps identity, gets hostbased client name, creates a short kernel handle, serializes context material, downcalls the credential/context tuple, and sends the null reply. Error paths delete partial contexts and send failure status with null buffers.

State and persistence: static `handle_seq` issues process-local context handles. Kernel context/init caches persist accepted contexts and short-lived init replies. Dynamic GSS buffers, context tokens, names, and hostbased names are freed per request.

Dependencies and integration: integrates GSSAPI, kernel procfs RPC cache channels, `context.h` serialization, nfsidmap principal mapping, qword encoders, Kerberos enctype limiter, and mechanism-to-file mapping.

Risks: handle reuse after daemon restart is acknowledged; fixed-size token/handle buffers bound request sizes; failed downcalls are logged but do not prevent response send. Test signals include continuation and completion handshakes, malformed qword fields, unmapped principals mapping to anonymous uid/gid, group list truncation, enctype limiter failure, context serialization failure, and procfs write failure.
