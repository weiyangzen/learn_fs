# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal.h

## Role

`fcal.h` is a Fibre Channel Arbitrated Loop variant of the FC-PH definitions. It largely mirrors `fc.h` with fixed-width integer types for FC-AL/SOCAL use.

## Definitions

- Defines FC version and max payload size.
- Defines `fc_frame_header_t` with FC-2 bitfields and fixed-width exchange/offset fields.
- Provides same frame predicates for originator, unsolicited, first/last sequence, last frame, and initiative.
- Defines `r_ctl`, device-data, BLS/ELS/link-control, type, and `F_CTL_*` constants.
- Defines well-known addresses and busy/reject reason codes.
- Defines `aFC2_RJT_PARAM`, transfer-ready payload `aXFER_RDY`, generic ELS payload, and `fc_dataseg_t`.

## Relationship To `fc.h`

The file duplicates much of `fc.h` for FC-AL-era drivers. Differences are mostly type-width choices and a narrower payload set.
