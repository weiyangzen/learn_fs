# sources/user-network-fs/nfs-ganesha/src/RPCAL/rpc_tools.c

Purpose: provides RPC utility helpers, mainly transport type stringification, transport-address copying, and `io_data` XDR encode/decode/free support for scatter/gather NFS payloads.

Important APIs and types: `xprt_type_to_str()`, `copy_xprt_addr()`, `xdr_io_data()`, `release_io_data_copy()`, `io_data`, `struct xdr_uio`, `struct xdr_vio`, and ntirpc XDR extension macros such as `xdr_putbufs()`, `XDR_FILLBUFS()`, `XDR_IOVCOUNT()`, and RDMA data-position helpers.

Control flow: `xdr_io_data()` dispatches by XDR operation. Encode writes the data length, builds an `xdr_uio` over caller-provided iovecs, handles XDR 4-byte rounding by either extending the last buffer if capacity permits or adding an inline zero-padded extra buffer, optionally preserves a release callback copy for async sends, and submits buffers with `xdr_putbufs()`. Decode reads the length, handles zero-length data with an empty iovec, computes the stream/RDMA data position, either copies into one allocated buffer when iov count exceeds `IOV_MAX` or maps XDR buffers into iovecs, advances the stream past rounded data, and sets release behavior. Free invokes any release callback and frees the iovec.

State and persistence: no durable state. UIO reference counts and release callbacks control buffer lifetime across asynchronous transport send completion. Decode can point iovecs directly into XDR receive buffers unless it falls back to copying.

Dependencies and integration points: used by NFS READ/WRITE XDR in `xdr_nfs23.c` and likely NFSv4 payload paths. Integrates with `op_ctx->is_rdma_buff_used`, Ganesha allocation helpers, ntirpc transport buffer APIs, and duplicate request response free paths.

Risks: zero-copy decode ties iovec lifetime to XDR buffer lifetime; callers must finish before receive buffers disappear. Encode padding manipulates the last iovec tail and must respect `last_iov_buf_size`. Release callback ownership is subtle for async sends and RDMA buffers. Large iov counts trigger copy fallback and memory pressure.

Test signals: encode/decode zero-length, aligned, and unaligned payloads; multi-iovec payloads; last-buffer extension versus extra-padding-buffer path; copy fallback over `IOV_MAX`; RDMA buffer mode; release callback invocation exactly once; and XDR_FREE cleanup.
