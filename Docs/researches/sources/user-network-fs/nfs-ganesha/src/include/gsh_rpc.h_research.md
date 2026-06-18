# sources/user-network-fs/nfs-ganesha/src/include/gsh_rpc.h

Purpose: This header is Ganesha's central RPC include and utility surface, intentionally isolating direct TIRPC/RPC includes behind one project header.

Important APIs/types/functions: Lookahead flags describe request classes and `NFS_LOOKAHEAD_HIGH_LATENCY` identifies latency-heavy operations. XDR maximum constants bound arrays, strings, generic bytes, and IO bytes. GSS/Kerberos defaults and `nfs_krb5_parameter_t` are defined when GSSAPI is enabled. Utility APIs include `log_sperror_gss`, `str_gc_proc`, `copy_xprt_addr`, `display_xprt_sockaddr`, `xprt_type_to_str`, `xdr_READ4res_uio_setup`, global `ntirpc_pp`, `struct io_data`, and `xdr_io_data`.

Control flow: RPC service code includes this header, classifies decoded requests with lookahead flags, uses TIRPC transport helpers for addresses, and serializes scatter/gather IO through `io_data`.

State and persistence: Holds no persistent state except references to global TIRPC package params and Kerberos config structs. Runtime IO data may carry release callbacks for buffer ownership.

Dependencies and integration points: Includes project atomics before RPC headers to avoid name conflicts, then TIRPC, GSSAPI conditionals, utilities, memory, lists, logging, and worker threads. It feeds NFS protocol decoders, transports, GSS security, and XDR helpers.

Risks: XDR limits are security and resource controls; changing them affects memory exposure. Include ordering protects against header name collisions. IO release callbacks must match buffer ownership.

Test signals: Build with/without GSSAPI and RDMA, validate XDR size enforcement, display local/remote transport addresses, test lookahead classification, serialize/deserialize `io_data`, and check Kerberos default config.
