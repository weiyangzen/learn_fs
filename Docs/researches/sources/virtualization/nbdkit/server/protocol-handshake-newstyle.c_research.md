# File Research: sources/virtualization/nbdkit/server/protocol-handshake-newstyle.c

This file implements the server side of NBD fixed-newstyle negotiation. It sends the initial newstyle magic/version/global flags, receives client flags, validates them against `mask_handshake`, then runs the option negotiation loop.

The option loop is bounded by `MAX_NR_OPTIONS`, with extra allowance after `NBD_OPT_LIST` based on the number of advertised exports. It validates option magic/version, rejects overlarge payloads, and handles clients without `NBD_FLAG_FIXED_NEWSTYLE` by only permitting `NBD_OPT_EXPORT_NAME`.

Implemented options include `NBD_OPT_EXPORT_NAME`, `NBD_OPT_ABORT`, `NBD_OPT_LIST`, `NBD_OPT_STARTTLS`, `NBD_OPT_INFO`, `NBD_OPT_GO`, `NBD_OPT_STRUCTURED_REPLY`, `NBD_OPT_LIST_META_CONTEXT`, and `NBD_OPT_SET_META_CONTEXT`. Unknown options receive `NBD_REP_ERR_UNSUP` after draining payload.

TLS policy is enforced before ordinary option processing. In `--tls=require`, only `NBD_OPT_ABORT` and `NBD_OPT_STARTTLS` are accepted before upgrade. `NBD_OPT_STARTTLS` replies in cleartext first, then calls `crypto_negotiate_tls`, marks the connection TLS-enabled, and wipes cached negotiation state such as structured replies, default export names, and meta-context selection.

Export selection is deferred until `finish_newstyle_options`, which copies the client export name, invalidates a prior meta-context if it was negotiated for a different export, calls `protocol_common_open`, and stores export flags in `conn->eflags`. `NBD_OPT_INFO` opens the backend temporarily, sends mandatory `NBD_INFO_EXPORT`, optionally replies with name, description, and block-size information, ACKs, then finalizes and closes. `NBD_OPT_GO` follows the same info reply path but keeps the export open for data phase.

Metadata context support is intentionally narrow. The server supports `base:allocation`, can list it, can set it only after structured replies are negotiated, stores the export name used for `SET_META_CONTEXT`, and marks `conn->meta_context_base_allocation` when the context is active. The negotiated context id is `base_allocation_id`.

String validation rejects names or queries over `NBD_MAX_STRING`, over their containing payload, or containing embedded NUL bytes. UTF-8 validity is noted as a TODO. Error replies may include the thread-local last error if short enough for the NBD string limit.

Important integration points are `protocol_common_open`, `backend_list_exports`, `backend_default_export`, `backend_export_description`, `backend_block_size`, `crypto_negotiate_tls`, connection send/recv methods, and connection fields later consumed by `protocol.c` (`structured_replies`, `eflags`, `meta_context_base_allocation`).
