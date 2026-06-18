# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfbcp.c

Implements BCP and TBCP filter creation.

Operators:
- `BCPEncode`
- `BCPDecode`
- `TBCPEncode`
- `TBCPDecode`

Encode filters use `filter_write_simple()` with the BCP/TBCP encode templates. Decode filters initialize `stream_BCPD_state` with null handlers for out-of-band `signal_interrupt` and `request_status`, then call `filter_read()` with the appropriate decode template.

The null handlers always return success and ignore those BCP signal paths.

Registered as filter operators in `zfbcp_op_defs`.
