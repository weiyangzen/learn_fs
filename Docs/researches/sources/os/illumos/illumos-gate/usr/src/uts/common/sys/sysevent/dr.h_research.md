# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dr.h

## Purpose
Defines dynamic reconfiguration sysevent attribute names, values, and helper conversions for attachment-point, request, and target-state events.

## Main Interfaces
- Attachment point attributes and values:
  - `DR_AP_ID`
  - `DR_HINT`
  - `DR_HINT_INSERT`
  - `DR_HINT_REMOVE`
  - `DR_RESERVED_ATTR`
- Hint constants and converter:
  - `SE_NO_HINT`
  - `SE_HINT_INSERT`
  - `SE_HINT_REMOVE`
  - `SE_HINT2STR(h)`
- Request attributes and values:
  - `DR_REQ_TYPE`
  - `DR_REQ_INCOMING_RES`
  - `DR_REQ_OUTGOING_RES`
  - `DR_REQ_INVESTIGATE_RES`
  - `SE_REQ2STR(h)`
- Target attribute:
  - `DR_TARGET_ID`

## Dependencies And Relationships
Schema comments cover `EC_DR` subclasses for attachment-point state changes, DR requests, and target state changes. Producers include DR subsystems and drivers.

## Research Notes
The header states that public DR sysevent schema changes require PSARC approval, so these string values are compatibility-sensitive.
