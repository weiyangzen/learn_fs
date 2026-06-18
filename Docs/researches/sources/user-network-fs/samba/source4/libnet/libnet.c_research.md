<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.c -->
# sources/user-network-fs/samba/source4/libnet/libnet.c

Purpose: initializes a source4 `libnet_context` with event, loadparm, resolver, and default SAMR state.

Important APIs and types: `libnet_context_init`, `struct libnet_context`, `tevent_context`, `loadparm_context`, `dcerpc_init`, and `lpcfg_resolve_context`.

Control flow: the function requires a non-NULL event context, allocates a zeroed context under the caller memory context, stores event and loadparm pointers, initializes DCERPC globally, derives the resolve context from loadparm, sets `samr.buf_size` to 128, and returns the context.

State and persistence: the returned context persists caller credentials, SAMR/LSA connection fields, resolver context, server address override, and event/loadparm pointers. This function only seeds default fields; connections and handles are opened later by other libnet calls.

Risks: NULL loadparm is not rejected before `lpcfg_resolve_context(lp_ctx)`, so callers must supply a valid loadparm context. `dcerpc_init` is global initialization. Test signals include NULL event rejection, valid context defaults, resolver construction, and subsequent SAMR calls using default buffer size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.c -->
