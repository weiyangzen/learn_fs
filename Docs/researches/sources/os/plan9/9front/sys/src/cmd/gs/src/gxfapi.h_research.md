# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.h

This small header declares the UFST callback installation/reset functions implemented by `gxfapi.c`.

`gx_set_UFST_Callbacks` accepts function pointers for `PCLEO_charptr`, `PCLchId2ptr`, and `PCLglyphID2Ptr`. `gx_reset_UFST_Callbacks` restores default callbacks. The types (`LPUB8`, `UW16`, `IF_STATE`) come from the UFST headers included by users of this header.

Filesystem relevance: none. It is font API integration.
