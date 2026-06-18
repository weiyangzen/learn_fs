# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/altsctr.h

## Scope

Complete file read, 84 lines. This header defines the alternate-sector partition metadata used by legacy DKTP disk handling.

## Public Surface

It exports:

- `struct alts_parttbl`: alternate sector table header with sanity/version fields, map location/length, remap-entry region metadata, reserved region base, and padding.
- `struct alts_ent`: one bad-sector remap range, with `bad_start`, `bad_end`, and `good_start`.
- Size macros `ALTS_PARTTBL_SIZE` and `ALTS_ENT_SIZE`.
- Sector-map states `ALTS_GOOD` and `ALTS_BAD`.
- Table identity/version constants `ALTS_SANITY` and `ALTS_VERSION1`.
- Entry/search constants `ALTS_ENT_EMPTY`, `ALTS_MAP_UP`, and `ALTS_MAP_DOWN`.

## Behavior And Integration

There is no executable code. Disk drivers and bad-block handlers use these structures to locate an alternate-sector partition map and translate bad sectors to reserved good sectors.

## Dependencies And Invariants

The file assumes fixed-width `uint32_t` is available before or through includers. On-disk consumers must preserve structure widths and offsets. `ALTS_SANITY` and `ALTS_VERSION1` are the primary validation fields.

## Risks

`ALTS_ENT_EMPTY` and `ALTS_MAP_DOWN` are negative macros while the table fields are unsigned, so callers must avoid storing sentinel values directly into `uint32_t` fields without deliberate casting semantics.
