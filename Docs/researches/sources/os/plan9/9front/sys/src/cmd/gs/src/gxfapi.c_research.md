# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.c

This file provides UFST font API callback dispatch support. It includes Ghostscript base headers and UFST headers, then defines callback stubs and mutable callback function pointers.

The three callbacks are `PCLEO_charptr`, `PCLchId2ptr`, and `PCLglyphID2Ptr`. By default they dispatch to private stubs returning NULL. `gx_set_UFST_Callbacks` installs caller-provided callback functions, and `gx_reset_UFST_Callbacks` restores the NULL stubs.

The comments note the callback pointers are static until graphics-library reentrancy and UFST callback reentrancy are fixed. That means this dispatcher is global process state rather than per-context state.

Filesystem relevance: none. It is font callback plumbing.
