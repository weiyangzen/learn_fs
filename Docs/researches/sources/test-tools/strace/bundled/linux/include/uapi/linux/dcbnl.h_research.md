# sources/test-tools/strace/bundled/linux/include/uapi/linux/dcbnl.h

Purpose: defines the Data Center Bridging generic netlink ABI for IEEE 802.1Qaz, QCN, PFC, CEE DCBX, application priority mappings, feature flags, and capability negotiation.

Important APIs/types/functions: structs include `ieee_ets`, `ieee_maxrate`, `ieee_qcn`, `ieee_qcn_stats`, `ieee_pfc`, `dcbnl_buffer`, `cee_pg`, `cee_pfc`, `dcb_app`, `dcb_peer_app_info`, and `dcbmsg`. Command enum `dcbnl_commands` covers get/set state, priority groups, PFC, capabilities, traffic class counts, BCN, APP, IEEE set/get/delete, DCBX, feature config, and CEE aggregate get. Many nested attr enums define IEEE, CEE, PFC, PG, TC, capability, number-of-TCs, BCN, APP, and feature-config attributes.

Control flow: no implementation exists here. The ABI flow is generic-netlink request/reply using `dcbmsg.cmd` and nested attributes. Some commands configure pending state and `DCB_CMD_SET_ALL` applies changes to hardware.

State and persistence behavior: represents live NIC/LLDP/DCBX negotiation state and driver configuration, not disk persistence. Struct fields encode traffic-class arrays with fixed maxima of eight priorities/classes and persistent-in-device settings only insofar as a driver/firmware stores them.

Dependencies: includes `<linux/types.h>` and relies on generic netlink/nested-attribute conventions outside the file.

Integration points: strace decodes DCB netlink commands and nested attributes. Network configuration tools use these IDs for configuring ETS/PFC/APP behavior and reading peer-advertised CEE/IEEE state.

Risks: several enums use dense priority-specific ranges plus `*_ALL` pseudo-attributes, so decoders must preserve order. IEEE and CEE selectors use overlapping but different semantic values. Comments for BCN get/set are historically confusing, so tests should check numeric IDs rather than prose assumptions.

Test signals: decode samples should include `DCB_CMD_IEEE_GET` with ETS/PFC/APP nested payloads, `DCB_CMD_CEE_GET`, capability flags, feature flags, and APP selector cases including DSCP and nonstandard PCP.
