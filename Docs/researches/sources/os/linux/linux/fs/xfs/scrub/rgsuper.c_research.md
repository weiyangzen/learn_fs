# File Research: sources/os/linux/linux/fs/xfs/scrub/rgsuper.c

## Purpose
Scrubs and repairs realtime group superblock metadata. Current checking is limited to rtgroup 0 and primarily cross-references metadata ownership because the rt superblock was already validated at mount time.

## Major Components
- `xchk_setup_rgsuperblock`: allocates a zero-block transaction.
- `xchk_rgsuperblock_xref`: verifies rt block 0 is used and owned by filesystem metadata.
- `xchk_rgsuperblock`: top-level scrub entry.
- `xrep_rgsuperblock`: logs the superblock during online repair.

## Control Flow and Invariants
Only realtime group 0 is accepted; other group numbers return `-ENOENT`. The scrubber obtains an existing rtgroup reference, locks the rtbitmap shared, then cross-references:
- block 0 is used realtime space;
- block 0 is owned only by `XFS_RMAP_OINFO_FS`.

Repair asserts group 0 and logs the superblock.

## Dependencies and Integration
Uses realtime group helpers, rtbitmap locking, rmap xref helpers from `rtrmap.c`, and used-space xref from `rtbitmap.c`.

## Risk and Edge Cases
The scrubber intentionally does not revalidate superblock contents beyond mount-time validation. Its value is cross-reference consistency with realtime space and rmap metadata.
