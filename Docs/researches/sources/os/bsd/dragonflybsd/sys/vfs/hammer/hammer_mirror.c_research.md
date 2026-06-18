# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mirror.c

## Purpose
Implements HAMMER mirror read/write ioctls that serialize modified B-tree records to userland and apply mirror streams to a target PFS.

## Key Elements
- `hammer_ioc_mirror_read()` scans a PFS-localized B-tree range with mirror-TID filtering and emits aligned mirror records into a user buffer.
- Emits `REC`, `PASS`, and `SKIP` records. Internal B-tree mirror-filter hits become skip ranges; older records become pass records so the receiver can delete gaps.
- Optionally omits bulk data with `HAMMER_IOC_MIRROR_NODATA`.
- Handles data CRC-domain errors as non-fatal stream flags so userland can wash or report damaged data.
- `hammer_ioc_mirror_write()` validates stream records, checks space/flusher pressure, and applies skip, record, and pass records.
- Write helpers delete target records absent from the source, create missing records, and update existing records only by delete TID.
- Filters non-mirrored record types, currently excluding cleanup config records.

## Dependencies
Uses HAMMER cursor/B-tree APIs, mirror-filter cursor state, CRC helpers, copyin/copyout, PFS localization helpers, flusher pressure checks, space checks, and generic record create/delete helpers in `hammer_object.c`.

## Behavior/Risks
Mirror write always returns `0` to preserve updated continuation fields and records cumulative failures in `mirror->head`. The stream is sensitive to localization remapping and record ordering. Bad data CRC records may be ignored on write. Correct deletion depends on careful cursor progress through `key_cur`, `ATEDISK`, skip boundaries, and `tid_end`.
