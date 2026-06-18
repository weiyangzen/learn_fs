# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/edisk.c

## Purpose
Implements `disk/edisk`, the GPT partition-table editor. It plugs GPT-specific parsing, mutation, printing, and writeback into the shared partition editor in `edit.c`.

## Key Behavior
- Defines on-disk GPT header and entry layouts, little-endian helpers, CRC32 calculation, UUID formatting/generation, GPT type-name mapping, and attribute flag formatting.
- Opens a disk or regular file, optionally overrides sector size, reads an existing GPT unless `-b` requests a blank table, and then runs the shared interactive command loop.
- Validates the protective MBR, detects dangerous hybrid MBR/GPT layouts, and refuses to edit when non-protective DOS partitions are present.
- Reads primary or backup GPT headers, validates header/table CRCs, restores a missing/mismatched counterpart header, and builds sorted in-memory `Gptpart` entries.
- Creates a blank GPT with 128 entries, a protective MBR, new disk GUID, primary header at LBA 1, backup header at the last LBA, and table areas around both headers.
- Writes primary and backup partition entry arrays, recalculates table/header CRCs, flushes changed cached sectors, and attempts to roll back already-written sectors on write failure.
- Implements auto partitioning that adds an ESP capped at 550 MB and a Plan 9 partition in the largest free span when missing.
- Provides GPT-specific editor commands: `t` sets partition type, `f` toggles GPT attributes, and `l` sets the UTF-16LE partition label.
- Prints user-facing summaries with attribute letters, GPT slot names (`pN`), LBAs, byte-scaled sizes, type aliases, and labels.
- Generates unique Plan 9 kernel partition names from GPT type aliases for `ctl` updates, avoiding duplicate names by suffixing.

## Interfaces And Dependencies
- Uses the shared `Edit` API from `edit.h`: `.add`, `.del`, `.ext`, `.help`, `.okname`, `.sum`, `.write`, and `.printctl`.
- Uses Plan 9 disk helpers from `<disk.h>` such as `opendisk()` and disk geometry/ctl fields.
- Uses `<mp.h>` and `<libsec.h>` for random UUID generation through `genrandom()`.
- Updates the active kernel disk partition table via `ctldiff()` after successful GPT writes.

## Notes
This file is deliberately conservative around MBR/GPT coexistence and backup-header recovery. The cached-sector writeback path is important because GPT writes span multiple sectors and a partial write would leave a conflicting table pair.
