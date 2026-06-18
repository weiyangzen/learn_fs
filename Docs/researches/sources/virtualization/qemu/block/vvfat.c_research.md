# File Research: sources/virtualization/qemu/block/vvfat.c

QEMU `vvfat` block/protocol driver that exposes a host directory as a synthetic FAT disk image. It can run read-only directly over host files or writable through a temporary qcow overlay that is reconciled back to the host directory after consistency checks.

Key responsibilities:
- Parse `fat:` filenames and runtime options: `dir`, `fat-type`, `floppy`, `label`, and `rw`.
- Build an in-memory MBR, boot sector, FAT, root directory, directory entries, and cluster-to-host-file mappings from a host directory tree.
- Generate FAT short names and long filename entries, including UTF-8/UTF-16 conversion, 8.3 lossy conversion, numeric tails, checksums, timestamps, and volume labels.
- Serve sector reads from synthetic first sectors, FAT copies, directory arrays, host file clusters, or the qcow write overlay.
- In writable mode, create a temporary qcow write target backed by the virtual `fat:` image, stage guest writes there, and try to commit changes back to host files/directories.
- Validate modified FAT and directory state before commit, including used-cluster tracking, long/short filename parsing, directory recursion, file size versus FAT chain length, duplicate cluster detection, and filename validity.
- Reconcile guest changes by scheduling and applying renames, mkdirs, new files, writeouts, and deletes.
- Register the `vvfat` format/protocol driver and private qcow child permissions.

Important structures:
- `bootsector_t`, `mbr_t`, `partition_t`, `direntry_t`: packed FAT/MBR on-disk structures synthesized in memory.
- `array_t`: small growable array used for FAT, directory, mapping, and commit lists.
- `mapping_t`: maps a FAT cluster range to a host file or directory segment.
- `BDRVVVFATState`: full driver state, geometry, FAT/directory/mapping arrays, current open host file, qcow overlay, commit list, used cluster map, and migration blocker.
- `commit_t`: queued host-side operation for rename, writeout, new file, or mkdir.
- `long_file_name`: parser state for VFAT long filename chains.

Core flow:
- `vvfat_open()` parses options, chooses floppy/disk geometry and FAT type, enables write target if requested, calls `init_directories()`, optionally initializes MBR, and installs a migration blocker for rw mode.
- `init_directories()` scans the host tree, builds directory entries and mappings, allocates FAT chains, fills boot sector fields, and establishes root mapping.
- `vvfat_read()` resolves sectors to first sectors, FAT copies, directory clusters, host file data, or qcow overlay data.
- `vvfat_write()` rejects protected boot-sector/FAT misuse, enforces read-only host-file constraints, writes sectors to qcow, marks modified clusters, and invokes `try_commit()`.
- `is_consistent()` copies the modified FAT from the overlay, marks existing mappings deleted, recursively checks the root directory, and verifies used cluster counts.
- `do_commit()` applies scheduled filesystem mutations, copies the modified FAT into the live FAT, commits directory entries and file contents, deletes removed mappings, empties qcow, and clears used-cluster state.

Notable constraints and risks:
- FAT32 is warned as untested and several comments note FAT32-specific inaccuracies.
- Writable mode is conservative and fragile: many inconsistency paths abort or refuse to commit.
- Writes are sector-aligned only; request alignment is forced to 512 bytes.
- Host files larger than 2 GiB are rejected while building mappings.
- Live migration is blocked only when writable qcow mode is enabled.
- The driver deliberately protects boot sectors, read-only files, and read-only directory entries from guest writes.
