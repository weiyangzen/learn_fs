# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex_devctl.h

This IB nexus devctl ABI header defines cfgadm attachment-point commands, user/kernel ioctl payloads, and HCA/port query structures.

Core definitions:
- APID types distinguish base, HCA, dynamic IOC/DLPI, and unknown attachment points.
- Dynamic APIDs use `"::"` as separator; strings name fabric, VPPA, port, and HCA service nodes.
- Service parser enum covers `name`, `class`, port service list, VPPA service list, HCA service list, and none.
- nvlist key strings identify node info, APID, type, receptacle/occupant state, and condition.
- Devctl subcommands cover node counts, snapshot size/get, dynamic device path size/get, HCA client list size/info, unconfigure client size/info, PKey table update, config-file service add/delete, verbose HCA info size/data, and IOC config update.
- `ibnex_ioctl_data_t` and `_32_t` carry command, buffer, buffer size, AP ID pointer/length, and misc arg for `DEVCTL_AP_CONTROL`.
- General ioctl codes expose API version, HCA GUID list, HCA query, and HCA port query through `/devices/ib:devctl`.
- API version is `1`.

HCA query ABI:
- `ibnex_ctl_hca_info_t` and 32-bit variant expose node/system-image GUIDs, port count, driver identity, device path pointer/length, capability flags, vendor/device/version IDs, channel/CQ/SGL/memory/window/RDMA/multicast/partition/PD/SRQ/FMR/LSO/inline/CQ moderation limits, firmware version, and detailed WQE sizes.
- Query wrapper supplies target HCA GUID and user-allocated device-path buffer.

Port query ABI:
- `ibnex_ctl_hca_port_info_t` and 32-bit variant expose LID, violation counters, SM SL/LID, physical/link state, port number, width/speed support/enabled/active, MTU, LMC, SGID/PKey table pointers and sizes, default PKey index, max VL, init type reply, subnet timeout, port capabilities, and max message size.
- Query wrapper supplies target HCA GUID/port plus user-allocated SGID and PKey tables.

Risk-sensitive invariants:
- Pointer-bearing structures have explicit 32-bit variants for 32-bit apps on a 64-bit kernel.
- User buffers are size-negotiated; insufficient buffers return lengths and/or NULL pointers rather than full data.
- The ioctl namespace deliberately avoids collision with generic devctl AP commands.
