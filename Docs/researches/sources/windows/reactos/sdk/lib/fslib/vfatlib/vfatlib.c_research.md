# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.c

Top-level ReactOS VFAT format and check API.

Key elements:
- Globals bridge checker state: `ChkdskCallback`, `FsCheckFlags`, `FsCheckMemQueue`, `FsCheckTotalFiles`.
- `VfatFormat` opens the volume, queries geometry/partition information, selects FAT12/16/32, locks the volume, dispatches to the formatter, dismounts/unlocks, and closes.
- FAT type selection uses existing MBR partition type when known, otherwise partition size/start-offset heuristics; GPT is size-based with a 32 GiB FAT limit.
- `UpdateProgress` converts sector increments into callback progress percentages.
- `VfatPrintV` and `VfatPrint` route checker/formatter text to FMIFS output callbacks.
- `VfatChkdsk` wires ReactOS parameters into the dosfstools-derived checker: open, dirty check, boot/FAT/root scan, bad-cluster scan, reclaim, free-count update, verification, optional commit, reporting, dismount/unlock, close.

Dependencies:
- Calls `Fat12Format`, `Fat16Format`, `Fat32Format`.
- Calls checker functions declared through `check/dosfsck.h` and related headers: `read_boot`, `read_fat`, `scan_root`, `fix_bad`, `reclaim_file`, `reclaim_free`, `update_free`, `file_unused`, `qfree`, `fs_*`.

Research notes:
- `VfatChkdsk` sets read-write only when `FixErrors` is true; otherwise it can detect dirty/corrupt state without committing changes.
- If `fs_open` fails with access denied, it asks the callback via `VOLUMEINUSE` whether to continue.
- There is a risky cleanup path: after failed `fs_open`, it calls `fs_close(FALSE)` even though a valid handle may not exist.
