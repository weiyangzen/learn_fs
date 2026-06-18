# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_blacklist.h

## Role

Small SATA framework header containing a blacklist for port multipliers that report faulty port counts in GSCR2.

## Key Elements

- Defines `sata_pmult_bl_t` with GSCR0, GSCR1, GSCR2, and flags fields.
- Defines `sata_pmult_blacklist[]` entries for Silicon Image 3726, 4726, and 4723 port multipliers.
- The comments state these devices report pseudo-port counts due to vendor configuration; the table records the actual usable port count in `bl_flags`.

## Dependencies and Coupling

Used by SATA port-multiplier discovery logic that interprets GSCR registers. The table is defined in the header, so inclusion must be controlled to avoid duplicate definitions.

## Research Notes

This is a hardware quirk table, not a generic policy module. It corrects known bad GSCR2 values during enumeration.
