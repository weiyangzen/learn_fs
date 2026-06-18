# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/fat.c

## Scope

FAT table decoder, comparator, validator, writer, and lost-chain checker for `fsck_msdos`.

## Main APIs

- `readfat()` reads one FAT copy and decodes FAT12/16/32 entries into `struct fatEntry`.
- `comparefat()` merges differences between FAT copies.
- `checkfat()` builds chain ownership/length metadata and detects loops, invalid endings, and crosslinks.
- `writefat()` encodes internal FAT state to all FAT copies.
- `checklost()` finds chains not referenced by directories and reconnects or clears them.
- `clearchain()` clears a chain; `rsrvdcltype()` formats reserved/bad/free/EOF state.

## Control Flow

`readfat()` validates the initial media/EOF byte sequence, decodes entries according to `ClustMask`, normalizes reserved values, counts free/bad clusters, and repairs invalid continuations by truncating when approved.

`comparefat()` scans all clusters and calls `clustdiffer()` to resolve mismatched free/reserved/EOF/continuation values. `checkfat()` first marks each chain head and length, then follows each chain to detect non-EOF endings, loops, out-of-range links, reserved/free terminations, and crosslinked chains. `tryclear()` prompts to clear or truncate damaged chains.

`writefat()` re-encodes FAT12 packed entries, FAT16 words, or FAT32 low 28-bit entries to every FAT copy and recomputes free count. `checklost()` scans unreferenced chain heads, asks to reconnect through `reconnect()` or clear, and repairs FAT32 FSInfo free/next values.

## Dependencies

- Uses `struct bootblock` and `struct fatEntry` from `dosfs.h`.
- Calls directory reconnect code in `dir.c`.
- Uses prompt and warning helpers from `fsutil`.

## Risks And Edge Cases

- FAT12 packing advances two clusters per three bytes and must preserve odd/even nibble layout.
- Crosslink repair may require reassigning common-chain `head` values when one chain is cleared and another retained.
- FSInfo is repaired after lost-chain handling, using the recomputed `NumFree`.
