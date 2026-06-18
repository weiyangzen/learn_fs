# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/ipmp.h

## Purpose
Defines Sun-private IPMP sysevent channel, payload attribute names, versions, and enumerations for group, interface, member, and probe events.

## Main Interfaces
- Event channel: `IPMP_EVENT_CHAN`.
- Common/event version attributes:
  - `IPMP_EVENT_VERSION`
  - `IPMP_EVENT_CUR_VERSION`
- Group state/change attributes:
  - `IPMP_GROUP_NAME`
  - `IPMP_GROUP_SIGNATURE`
  - `IPMP_GROUP_STATE`
  - `IPMP_GROUPLIST_SIGNATURE`
  - `IPMP_GROUP_OPERATION`
- Enums for group state and group operation.
- Interface/member attributes:
  - `IPMP_IF_OPERATION`
  - `IPMP_IF_NAME`
  - `IPMP_IF_TYPE`
  - `IPMP_IF_STATE`
- Enums for interface operation, type, and state.
- Probe attributes:
  - `IPMP_PROBE_ID`
  - `IPMP_PROBE_STATE`
  - probe timing fields
  - `IPMP_PROBE_TARGET`
  - RTT average/deviation attributes
- Probe state enum.

## Dependencies And Relationships
Schema comments map these payloads to `EC_IPMP` subclasses in `eventdefs.h`. The publisher is `in.mpathd`.

## Research Notes
The header states these definitions are private and subject to change. The schema is still important for IPMP event consumers that bind to the named channel.
