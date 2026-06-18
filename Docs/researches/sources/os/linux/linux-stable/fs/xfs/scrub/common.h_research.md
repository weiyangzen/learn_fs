# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/common.h

## Role

Shared scrub helper header. It declares common setup routines, error processors, outcome flag helpers, AG/rtgroup resource helpers, inode helpers, xref controls, and metadata inode utilities.

## Key Definitions

- `xchk_setup_nothing()` is the disabled-feature setup fallback.
- `xchk_ag_init_existing()` and `xchk_rtgroup_init_existing()` treat missing referenced groups as corruption.
- `XCHK_RTGLOCK_ALL` groups all realtime metadata locks.
- `xchk_iget_safe()` wraps untrusted inode lookup in a temporary scrub transaction.
- `xchk_skip_xref()` suppresses xref checks after primary or xref corruption is already known.
- `xchk_needs_repair()` and `xchk_could_repair()` encode repair decision predicates.
- `xchk_need_intent_drain()` identifies when expensive intent-drain hooks are warranted.

## API Surface

Exports transaction, setup, AG/rtgroup, inode, lock, buffer verifier, filesystem gate, metadata inode, and directory/zapped-state helper APIs for the scrub subsystem.

## Research Notes

The header is the main dependency surface for individual scrubbers. Feature-specific setup functions are compiled out to `xchk_setup_nothing` when quotas or realtime support are absent.
