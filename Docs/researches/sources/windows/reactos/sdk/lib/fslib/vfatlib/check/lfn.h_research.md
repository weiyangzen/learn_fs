# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.h

Declares the VFAT long-filename parser and repair helpers.

Key elements:
- `lfn_reset` clears parser state.
- `lfn_add_slot` processes one VFAT LFN directory slot.
- `lfn_get` returns the reconstructed long name for a matching short entry.
- `lfn_check_orphaned` handles unfinished/unattached long-name state.
- `lfn_fix_checksum` repairs checksum bytes over a slot range.

Dependencies:
- Requires `DIR_ENT` and `off_t` from surrounding checker headers.

Research notes:
- This header exposes a small state-machine API; callers must preserve directory-entry ordering.
