# sources/user-network-fs/samba/source3/lib/netapi/wkstainfo.c

## Purpose
This file implements `NetWkstaGetInfo` for source3 libnetapi. It exposes workstation metadata levels 100, 101, and 102 by calling the WKSSVC RPC endpoint and mapping generated `wkssvc_NetWkstaInfo` unions into libnetapi `WKSTA_INFO_*` output buffers.

## Important APIs, Types, And Functions
`NetWkstaGetInfo_l()` redirects local calls to localhost. `NetWkstaGetInfo_r()` validates `r->out.buffer`, accepts only levels 100, 101, and 102, obtains a WKSSVC binding handle with `libnetapi_get_binding_handle()`, calls `dcerpc_wkssvc_NetWkstaGetInfo()`, and maps RPC output through `map_wksta_info_to_WKSTA_INFO_buffer()`. The mapper populates platform id, computer name, workgroup/domain, version major/minor, LAN root for 101/102, and logged-on user count for 102.

## Control Flow
The remote wrapper is linear: validate level, bind, call RPC, check both transport `NTSTATUS` and returned `WERROR`, then allocate the requested NetAPI structure into the caller's buffer with `ADD_TO_ARRAY`. Unsupported levels return `WERR_INVALID_LEVEL`; mapper unsupported cases return `NT_STATUS_NOT_SUPPORTED`, converted to `WERROR`.

## State And Persistence
The file has no durable state. Outputs are talloc-allocated from the libnetapi context passed to the mapper. Remote state is read-only workstation service state from the target server.

## Dependencies And Integration Points
It depends on generated libnetapi and WKSSVC NDR headers, source3 libnetapi binding helpers, and talloc array utilities. It includes smbconf headers but does not directly use smbconf functions in this file.

## Risks And Test Signals
Risk is modest: null `out.buffer`, level validation, correct union member use for each level, and string allocation failures. Tests should call levels 100/101/102 against a local server, verify fields are copied, verify invalid levels fail, and inject RPC/binding failures if the test harness supports mocks.
