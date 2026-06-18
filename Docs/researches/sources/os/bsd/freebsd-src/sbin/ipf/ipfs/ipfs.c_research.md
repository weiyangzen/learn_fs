# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/ipfs.c

## Purpose
Saves, restores, locks, unlocks, and edits IPFilter NAT/state table snapshots.

## Main Elements
- Command modes include lock/unlock, save/read all, save/read NAT only, save/read state only, dry-run, verbose, directory selection, file selection, and interface-name replacement.
- `changestateif()` and `changenatif()` rewrite saved interface names in state/NAT snapshot files.
- `setlock()` uses `SIOCSTLCK` to lock or unlock IPFilter state during save/restore.
- `writestate()` iterates live state entries with `SIOCSTGET` and writes fixed-size `ipstate_save_t` records.
- `readstate()` reads state records, tracks shared rule pointers, marks first rule references with `SI_NEWFR`, and restores entries with `SIOCSTPUT`.
- `writenat()` obtains NAT save-record sizes with `SIOCSTGSZ`, fetches entries with `SIOCSTGET`, and writes variable-size NAT records.
- `readnat()` reads variable-size NAT records, remaps shared rule references, and restores entries through `SIOCSTPUT`.
- `writeall()` and `readall()` operate in `/var/db/ipf` by default and lock IPFilter while saving/restoring state and NAT files.

## Dependencies And Integration
Uses IPFilter device nodes (`IPL_NAME`, `IPSTATE_NAME`, `IPNAT_NAME`), save ABI structures, and state/NAT ioctls. Default files are `ipstate.ipf` and `ipnat.ipf` under `/var/db/ipf`.

## Risk Notes
Snapshot files contain kernel pointer values that must be remapped during restore. Partial reads, variable-size NAT records, and lock/unlock error paths are important correctness risks.
