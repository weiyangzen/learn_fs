# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_if.h

## Role

iSCSI initiator management ioctl interface header. It defines user/kernel structures for target/session/login/discovery/authentication/configuration management.

## Key Elements

- Defines interface version and numeric login parameter IDs.
- Defines initiator devctl path and many ioctl command values for OID creation, login/logout, parameter get/set/clear, target/static/discovery management, CHAP/auth/RADIUS, LUN/connection queries, USCSI passthrough, SMF state, SendTargets, iSNS, config sessions, boot properties, tunables, target re-enumeration, and debug dump.
- Defines CHAP, target-list, static target, digest, and parameter-type constants.
- Defines discovery method enum with static, SLP, iSNS, SendTargets, and boot discovery.
- `iscsi_oid_t` identifies target objects by name/TPGT and returns an OID.
- `iscsi_login_params_t` stores negotiated/configured session and connection login parameters.
- `entry_t` describes a login endpoint, including IPv4/IPv6 address, port, TPGT, and boot-session flag.
- Defines structures for node names, min/max integer/bool parameter values, parameter get/set payloads, tunable object values, CHAP properties, auth properties, RADIUS properties, IP addresses, target addresses, address lists, target properties, target OID lists, static target properties, LUN properties/lists, connection properties/lists, discovery properties, USCSI passthrough, SendTargets results, static target entries, iSNS portal groups, configured session bindings, re-enumeration, and boot properties.
- Defines sysevent class/subclass strings for iSCSI discovery and property-change events.
- Under `_KERNEL`, declares filesystem/socket helper wrappers used by the iSCSI code.
- Declares common utility functions for IQN creation, bitmap printing, login parameter mapping, and address/port/TPGT parsing.

## Dependencies and Coupling

Includes networking, SCSI USCSI, and iSCSI protocol headers. The structures form an ioctl ABI consumed by management tools and kernel driver code.

## Research Notes

Most variable-length outputs use a one-element trailing array pattern with input/output counts. The file is intentionally broad because it centralizes management ABI for discovery, authentication, session binding, LUN visibility, and boot-time iSCSI configuration.
