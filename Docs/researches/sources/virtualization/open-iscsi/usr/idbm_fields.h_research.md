# File Research: sources/virtualization/open-iscsi/usr/idbm_fields.h

This header is the string schema for open-iscsi database records. It defines the exact key names used in persisted configuration files and in `recinfo_t` mappings.

Key field groups:
- Record framing: `ISCSI_BEGIN_REC`, `ISCSI_END_REC`.
- Node identity/startup/discovery fields: `node.name`, `node.tpgt`, startup, discovery address/port/type, boot LUN.
- Session fields: command sequencing, retry counts, queue depth, CHAP credentials, timeouts, iSCSI negotiation parameters, autoscan, and reopen settings.
- Connection fields: per-connection portal address/port, TCP window/TOS/congestion options, login/logout/auth/noop timeouts, digests, markers, and data segment lengths.
- Iface fields: binding identity, initiator name, ISID, IPv4/IPv6 address configuration, VLAN, TCP/network tuning, DHCP options, IPv6 neighbor/router behavior, and iSCSI offload/session knobs.
- Discovery fields: SendTargets and iSNS startup, type, address/port, auth, timeouts, discovery daemon controls, and receive segment length.
- Host CHAP fields: table index, auth method, usernames, passwords, and password lengths.
- Flashnode session and connection fields: firmware-backed discovery/session/portal flags, CHAP indexes and credentials, target metadata, boot target flag, per-connection digest/TCP/IP/VLAN-style parameters, statsn fields, and redirect/local addresses.

Important dependencies:
- Includes `version.h` for versioned begin-record markers.

Filesystem/storage relevance:
- This is the canonical on-disk/user-visible naming layer for iSCSI target, session, interface, and firmware flashnode configuration. Tools that create or mutate remote block-storage sessions depend on these exact strings.

Notable details:
- The iSNS address and port macros are defined as `discovery.sendtargets.address` and `discovery.sendtargets.port`, which may be intentional compatibility behavior or a schema typo. It is worth checking corresponding parser/serializer code before changing it.
- Many fields map to kernel IPC attributes later built in `iface.c` and `initiator_common.c`.
