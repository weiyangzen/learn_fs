# File Research: sources/local-fs/dosfstools/src/lfn.c

VFAT long-filename parser and repair helper.

Data model:
- Defines packed `LFN_ENT` for VFAT LFN slots.
- Maintains parser state in module globals:
  - `lfn_unicode`
  - `lfn_checksum`
  - `lfn_slot`
  - `lfn_offsets`
  - `lfn_parts`

Main functions:
- `cnv_unicode()` converts UTF-16LE LFN slot data to local multibyte text, falling back to Linux-style `:xxx` escapes for unconvertible characters.
- `lfn_fix_checksum()` recalculates and writes LFN alias checksums over a range of LFN slots.
- `lfn_reset()` clears parser state.
- `lfn_add_slot()` processes one LFN directory slot, detecting and optionally repairing:
  - nested/new LFN starts inside old sequence
  - missing start bit
  - wrong sequence numbers
  - checksum mismatches
  - nonzero reserved field
  - nonzero start-cluster field.
- `lfn_get()` attaches the accumulated LFN to the following short directory entry, handling unfinished sequences and checksum mismatch.
- `lfn_check_orphaned()` detects an LFN sequence not followed by a real short entry and can delete it.

Dependencies:
- Uses `fs_write()` for slot repairs.
- Uses `get_choice()` and `xasprintf()` for repair decisions.
- Uses `qalloc()` via `mem_queue` so returned LFN strings live for the current scan pass.
- Uses `file_name()` to describe short aliases.

Research notes:
- LFN parsing is intentionally stateful across sequential directory entries.
- Directory scanners must call `lfn_reset()` at new directory boundaries and `lfn_check_orphaned()` at sequence boundaries/end.
