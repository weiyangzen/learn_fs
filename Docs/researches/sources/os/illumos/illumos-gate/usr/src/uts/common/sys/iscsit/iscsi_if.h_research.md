# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsi_if.h

This header defines the ioctl/user-kernel interface for the illumos iSCSI initiator stack and related common utilities.

Interface constants:
- `ISCSI_INTERFACE_VERSION` is 3.
- `ISCSI_MAX_NAME_LEN` is 224.
- Login parameter numeric IDs for operational settings such as ordering, immediate data, InitialR2T, digest options, timers, segment lengths, burst lengths, max connections, outstanding R2T, and error recovery.
- Special parameter IDs for persistent DB entries, initiator name, and initiator alias.
- Driver devctl path constants.
- Ioctl command base and commands for OID creation, login/logout, parameter get/set/clear, target lists/properties/address, CHAP, static discovery, discovery settings, RADIUS, DB reload, LUN/connection lists/properties, USCSI, door handle, discovery events, auth settings, SendTargets, iSNS server settings, session config, initiator node name, and debug DB dump.
- Digest preference constants.

Core structs:
- `iscsi_oid_t` creates/returns target OIDs and carries target name and TPGT.
- `iscsi_login_params_t` stores all main session/connection operational parameters.
- `entry_t` describes a login/discovery endpoint with IPv4/IPv6 address, port, and TPGT.
- `node_name_t` stores initiator name/alias.
- Parameter get/set support: `iscsi_int_info_t`, `iscsi_bool_info_t`, `iscsi_get_value_t`, `iscsi_param_get_t`, `iscsi_set_value_t`, `iscsi_param_set_t`.

Authentication structs:
- `iscsi_chap_props_t` stores CHAP retry count, OID, username, and secret.
- `authMethod_t` includes none, CHAP, SRP, KRB5, SPKM1, SPKM2.
- `iscsi_auth_props_t` stores bidirectional-auth and method settings.
- `iscsi_radius_props_t` stores RADIUS address, port, shared secret, access/config flags, and secret length.

Address/discovery/target structs:
- `iscsi_ipaddr_t`, `iscsi_addr_t`, `iscsi_addr_list_t`.
- `iscsi_property_t` reports target name/alias, discovery method, connection status, connection count, last error, configured/negotiated TPGT, and ISID.
- `iscsi_target_list_t` and `iscsi_static_property_t`.
- Discovery enum `iSCSIDiscoveryMethod_t` and mask `ISCSI_ALL_DISCOVERY_METHODS`.

LUN/connection structs:
- `iscsi_lun_status_t`, inquiry ID length constants, `iscsi_lun_props_t`, `iscsi_if_lun_t`, `iscsi_lun_list_t`.
- `iscsi_conn_props_t`, `iscsi_if_conn_t`, `iscsi_conn_list_t`.

iSNS, USCSI, SendTargets:
- `isns_method_t`, `iSCSIDiscoveryProperties_t`.
- `iscsi_uscsi_t` and `_SYSCALL32` `iscsi_uscsi32_t`.
- `iscsi_sendtgts_entry_t`, `iscsi_sendtgts_list_t`, `iscsi_target_entry_t`.
- `isns_portal_group_t`, `isns_portal_group_list_t`, `isns_server_portal_group_list_t`.

Session config and events:
- Config session min/max and variable-sized `iscsi_config_sess_t`.
- `ISCSI_SESSION_CONFIG_SIZE(SIZE)` helper.
- Event class/subclass strings for static, SendTargets, SLP, iSNS, and property changes.

Kernel-only helpers:
- Under `_KERNEL`, declares file and socket utility wrappers used by `iscsid`: open/close/remove/rename/read/write/sendto/recvfrom and `iscsid_errno`.

Common utility prototypes:
- `utils_iqn_create`, `prt_bitmap`, `utils_map_param`, `parse_addr_port_tpgt`.

Dependencies:
- Kernel includes socket and STREAMS support headers.
- Includes `netinet/in.h`, `sys/scsi/impl/uscsi.h`, and `sys/iscsi_protocol.h`.

Relevance:
- Major control-plane ABI for network block storage discovery, login, authentication, target/session/LUN enumeration, and pass-through SCSI operations.
