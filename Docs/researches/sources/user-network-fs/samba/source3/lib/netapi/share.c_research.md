# Research: sources/user-network-fs/samba/source3/lib/netapi/share.c

Purpose: implements NetAPI share add/delete/enumerate/get/set operations over the SRVSVC RPC interface. It maps between public `SHARE_INFO_*` buffers and generated `srvsvc_NetShareInfo*` unions.

Important APIs/functions: `map_srvsvc_share_info_to_SHARE_INFO_buffer` converts SRVSVC levels 0, 1, 2, 501, and 1005 to public buffers. `map_SHARE_INFO_buffer_to_srvsvc_share_info` converts public levels 2, 502, and 1004 into SRVSVC input unions. Request handlers include `NetShareAdd_r/l`, `NetShareDel_r/l`, `NetShareEnum_r/l`, `NetShareGetInfo_r/l`, and `NetShareSetInfo_r/l`.

Control flow: add validates the input buffer and permits levels 2 and 502, rejects 503 as unsupported, obtains a SRVSVC binding, maps the buffer, and calls `NetShareAdd`. Delete validates `net_name` and calls `NetShareDel`. Enum validates levels 0-2, creates the matching SRVSVC share counter union, calls `NetShareEnumAll`, accepts success or `WERR_MORE_DATA`, and appends each returned item to the caller buffer. Get-info validates name/output/level and calls `NetShareGetInfo`. Set-info allows levels 2 and 1004, maps the buffer, and calls `NetShareSetInfo`.

State and persistence: add, delete, and set-info persist share configuration on the target server. Enumeration and get-info are read-only. The implementation itself keeps no durable state; output buffers are talloc arrays under `ctx`.

Dependencies/integration: depends on generated SRVSVC stubs, `ndr_security.h` for security descriptor sizing at level 502, and private NetAPI binding helpers. It is used by public `NetShare*` wrappers and by `tests/netshare.c`.

Risks: `NetShareEnum_r` loops with `info_ctr.ctr.ctr1->count` even when level 0 or 2 selected `ctr0` or `ctr2`; if the generated union does not alias counts compatibly this can crash or miscount. Level 502 can be sent for add but get/set level 502 are declared unsupported, so security descriptor round-tripping is incomplete. The level 502 mapping uses caller-provided security descriptor pointers and NDR size calculation; invalid descriptors may fail later in RPC marshalling. Local `_l` handlers just redirect to localhost, so there is no separate local smb.conf manipulation path in this file.

Test signals: tests should add/delete level 2 and level 502 shares, enumerate levels 0-2 with more-data resume, get levels 0/1/2/501/1005, set level 1004 comments, validate unsupported 502/503 cases, and specifically run level 0 and level 2 enumeration under sanitizers to catch the `ctr1->count` risk.
