# File Research: sources/virtualization/open-iscsi/usr/host.c

iSCSI host display and CHAP netlink configuration helper implementation.

The host-info path matches kernel iSCSI hosts to active sessions by mapping session SID to host number through sysfs, then prints host information in flat or tree forms. It formats transport, initiator name, IP address, hardware address, netdev, host state, per-host iface records, and optional session trees. IPv6 addresses are bracketed in output.

`host_info_print()` supports info levels 0 through 4. Level 0 / -1 prints flat host rows. Higher levels print tree output and progressively include session state, iface information, iSCSI parameters, SCSI devices, and kernel/userspace version information. It probes offload transports before tree enumeration.

The CHAP path builds netlink attributes for host CHAP records. `chap_fill_param_uint()` writes fixed-width integer values into `iscsi_param_info` attributes, supporting 1-, 2-, and 4-byte values. `chap_fill_param_str()` writes string attributes. `chap_build_config()` starts at iovec index 2 to leave room for netlink header and event slots, then appends index, CHAP type, username, password, and password length attributes.

Error handling returns open-iscsi error codes for invalid info levels, empty host lists, allocation failures, and sysfs enumeration failures. The CHAP helper returns a count of successfully built iovecs and silently skips fields that fail allocation.
