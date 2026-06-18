# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsit_common.h

## Role

`iscsit_common.h` defines the shared user/kernel configuration ABI for the illumos COMSTAR iSCSI target provider. It names the iscsit pseudo-device, ioctl commands, SMF/administration status values, nvlist property names, authentication mode strings, configuration object layouts, and conversion/free helpers used by management tools and the kernel driver.

## Major Definitions

The file defines API version `ISCSIT_API_VERS0`, the module/device names, service ioctl numbers, and `iscsit_hostinfo_t`, which carries a fully qualified host name for iSNS entity identifiers during service enable. `iscsit_ioc_set_config_t` and `iscsit_ioc_getstate_t` pass packed nvlists across the ioctl boundary, with `_SYSCALL32` variants using `caddr32_t` for 32-bit callers.

The configuration model is a linked-object graph:
- `it_tpgt_t` binds a target portal group name to an RFC 3720 target portal group tag and carries a generation counter.
- `it_tgt_t` represents an iSCSI target node, its TPGT list, and target nvlist properties such as target CHAP credentials, alias, and auth policy.
- `it_portal_t` stores a `sockaddr_storage` endpoint and links portal lists.
- `it_tpg_t` represents a named target portal group and its portal list.
- `it_ini_t` represents an initiator context and its CHAP properties.
- `it_config_t` aggregates the persistent STMF token, targets, TPGs, initiators, iSNS server portals, counts, and global properties.

The property macros define the string keys stored in nvlists: global and target auth/alias fields, CHAP credentials, RADIUS server/secret, iSNS enable/server settings, and target rename support.

## Interfaces

The header declares bidirectional conversion routines between C structures and nvlists for configs, target lists, targets, TPG tags, TPGs, initiators, and lists of each object type. It also declares lookup helpers for targets, TPGs, portals, and iSNS servers; sockaddr comparison and string conversion helpers; address-string parsing; array-to-portal-list conversion; recursive free helpers for each object family; and base64 encode/decode helpers for iSCSI secrets.

## Integration Notes

This is an ABI-sensitive header shared by userland administration code and the kernel. Structure sizes, ioctl values, property key strings, list ownership, and generation counters must remain compatible with existing management tools and the driver. Address parsing and nvlist conversion are central trust boundaries because malformed portal strings, packed nvlists, and credential fields cross between userland, persistent STMF provider data, and kernel state.
