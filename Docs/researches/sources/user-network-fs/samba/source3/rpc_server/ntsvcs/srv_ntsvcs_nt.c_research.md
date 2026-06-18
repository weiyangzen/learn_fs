# sources/user-network-fs/samba/source3/rpc_server/ntsvcs/srv_ntsvcs_nt.c

Purpose: implements a small compatibility subset of the Windows NTSVCS/Plug and Play RPC interface. It mostly returns plausible responses for service-backed legacy device queries and marks the rest of the PNP surface unsupported.

Important APIs and functions: `get_device_path()` formats `ROOT\Legacy_<service>\0000`. `_PNP_GetVersion()` returns version `0x0400`. `_PNP_GetDeviceListSize()` and `_PNP_GetDeviceList()` validate service-filter pointers, construct a legacy device path, and return size or multi-SZ encoded list data. `_PNP_GetDeviceRegProp()` supports `DEV_REGPROP_DESC` by parsing the service name from the device path, looking up the display name through `svcctl_lookup_dispname()`, and returning it as `REG_SZ`. `_PNP_ValidateDeviceInstance()`, `_PNP_GetHwProfInfo()`, and `_PNP_HwProfFlags()` return simple compatibility responses. Most other `_PNP_*` calls set `DCERPC_FAULT_OP_RNG_ERROR` and return `WERR_NOT_SUPPORTED`.

Control flow: clients can ask for a device list size, then list, then description property. The implementation uses registry encoding helpers (`push_reg_multi_sz`, `push_reg_sz`) to produce Windows-compatible string buffers and returns buffer-small errors with needed sizes.

State and persistence: no persistent state is stored. Data is synthesized from incoming service/device names and live service-control display-name lookup.

Dependencies: generated NTSVCS NDR compatibility glue, DCE/RPC call state for session info, service control winreg glue, and registry utility string encoders.

Risks: `_PNP_GetDeviceRegProp()` mutates `r->in.devicepath` in place while parsing by writing NUL terminators; this assumes the generated stub provides mutable storage. Device-list functions only emulate legacy service devices and do not enumerate real hardware. The many unsupported opnums are compatibility decisions and may affect clients expecting fuller PNP behavior.

Test signals: RPC tests should cover buffer sizing, multi-SZ encoding, display-name lookup success/failure, invalid pointer handling under `CM_GETIDLIST_FILTER_SERVICE`, and expected faults for unsupported PNP calls.
