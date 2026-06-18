# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_mad.h

## Scope

Defines common InfiniBand Management Datagram (MAD) wire-format constants and base structures used by multiple management classes.

## APIs And Structures

- `MAD_SIZE_IN_BYTES` sets the standard MAD size to 256 bytes.
- `ib_mad_hdr_t` defines the common 24-byte MAD header: base/class versions, class, method/response bit, status, class-specific field, transaction ID, attribute ID, and attribute modifier.
- Management class constants cover subnet management, subnet administration, performance, baseboard/device/communication management, SNMP, vendor, and application class ranges.
- Method/status constants define GET, SET, SEND, TRAP, REPORT, trap repress, response methods, and common MAD error statuses.
- Attribute IDs include ClassPortInfo, Notice, and InformInfo.
- `ib_mad_classportinfo_t`, `ib_mad_notice_t`, and `ib_mad_informinfo_t` model IB specification tables for class port info, notices/traps, and trap subscription info.

## Format Details

- Bitfield layouts are defined separately for `_BIT_FIELDS_HTOL` and `_BIT_FIELDS_LTOH`, with a compile-time error if neither endian bitfield convention is selected.
- ClassPortInfo stores redirect/trap GID, LID, P_Key, QP, Q_Key, SL, traffic class, flow label, and hop-limit details.
- Notice encodes generic/vendor notices, producer type or vendor ID, trap/device IDs, issuer identity, notice count/toggle, detail bytes, and issuer GID.
- InformInfo encodes GID/LID ranges, subscription mode, generic/vendor forwarding, trap type/number, destination QPN, response time, and producer type/vendor ID.

## Dependencies

- Includes `sys/ib/ib_types.h` for InfiniBand scalar and address types such as `ib_gid_t`, `ib_lid_t`, `ib_pkey_t`, and `ib_qkey_t`.
- Consumed by IBMF, IBCM, IBDM, IBDMA, and SA-related code that builds or parses management datagrams.

## Risks And Invariants

- These structures mirror on-wire formats; field order, widths, and endian-specific bitfields must remain ABI-compatible with the InfiniBand specification.
- MAD payload users must treat multi-byte fields as wire-format data where required by the surrounding protocol.
- The header intentionally uses C bitfields for packed protocol fields, so all builds must define the correct illumos bitfield ordering macro.
