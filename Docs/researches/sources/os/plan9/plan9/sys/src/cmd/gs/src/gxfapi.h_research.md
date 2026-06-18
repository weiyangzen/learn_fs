# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.h

Header for UFST font callback dispatch.

- Declares `gx_set_UFST_Callbacks`, accepting callback pointers for:
  - `PCLEO_charptr`
  - `PCLchId2ptr`
  - `PCLglyphID2Ptr`
- Declares `gx_reset_UFST_Callbacks`.

Dependencies: callback argument/return types such as `LPUB8`, `UW16`, and `IF_STATE` must be supplied by UFST-related includes before use.
