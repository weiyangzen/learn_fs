# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_ulpif.h

Defines the upper-layer protocol interface between fctl/fp and FC ULP modules such as FCP, FCIP, and FCSM. It provides ULP module revision constants, port attach/detach command enums, PLOGI behavior flags, device online/offline values, and port reset command codes.

Key structures are `fc_portmap_t`, `fc_ulp_port_info_t`, and `fc_ulp_modinfo_t`. `fc_ulp_modinfo_t` is the ULP callback vector for port attach/detach/ioctl, ELS callbacks, data callbacks, and state-change callbacks.

Exports include `fc_ulp_add/remove`, packet init/uninit, port map retrieval, login, remote-port lookup, name-service submission, transport, ELS issue, unsolicited buffer alloc/free/release, abort, link reset, port reset, error decoding, WWN/D_ID lookup, FCA device lookup, port notification, relogin disable/enable, port busy/idle, NPIV queries, and device-event logging.
