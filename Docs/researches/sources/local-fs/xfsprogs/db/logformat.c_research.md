# File Research: sources/local-fs/xfsprogs/db/logformat.c

## Purpose
Provides expert log reformatting plus informational log reservation commands.

## Main Interfaces
- `logformat_init()` registers expert-only `logformat`.
- `logres_init()` registers `logres` and `untorn_write_max`.
- `logformat [-c cycle] [-s sunit]` clears a clean log to a chosen cycle/stripe unit.
- `logres` prints all transaction reservation entries.
- `untorn_write_max -l logres|-b blocks` computes untorn-write reservation relationships for reflink filesystems.

## Control Flow
`logformat_f()` constructs enough `mp->m_log` state to call `xlog_find_tail`, refuses dirty logs, defaults unspecified cycle/sunit to current log values, and clears the log with `libxfs_log_clear`. `logres_f()` iterates the mount reservation table and prints the max transaction reservation. `untorn_cow_limits()` models the log space needed to finish BUI/RUI/CUI/EFI intent chains for software untorn-write emulation.

## Dependencies
Uses libxlog tail discovery, libxfs log clear/reservation calculators, mount superblock geometry, and output helpers.

## Risks And Invariants
- `logformat` is expert-only and refuses to format a dirty log; users must mount to replay first.
- Stripe unit must be block-aligned and, for log v2, at most 256 KiB.
- `untorn_write_max` only reports meaningful values when reflink is enabled.
