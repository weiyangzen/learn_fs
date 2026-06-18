# File Research: sources/os/bsd/freebsd-src/sbin/dump/main.c

Main program for UFS `dump`. It parses options, resolves the target filesystem/device, optionally creates a live filesystem snapshot, calculates dump scope and media estimates, then drives the four dump passes.

Key responsibilities:
- Defines most global state shared by the dump subsystem: maps, device/tape names, dump level, density, blocking factor, media sizing, cache size, remote host, timing, superblock pointer, and pass number.
- Parses current and obsolete dump option formats via `getopt()` and `obsolete()`.
- Handles output routing to tape path, stdout, remote tape, or a pipeline command.
- Resolves filesystem names through `fstab`, opens raw devices, and warns about dumping live read-write filesystems without `-L`.
- Creates `.snap/dump_snapshot` through `_PATH_MKSNAP_FFS` when `-L` is valid.
- Reads the UFS superblock with `sbget()` and initializes block-size shifts and inode maps.
- Runs pass I (`mapfiles`), pass II (`mapdirs` until stable), pass III directories, and pass IV regular files.
- Writes end markers, performance summaries, updates dumpdates, rewinds, broadcasts completion, and exits.

Option highlights:
- Levels `0` through `9`, incremental base via dumpdates unless `-T`.
- `-a`, `-B`, `-b`, `-c`, `-d`, `-s` control media sizing.
- `-f` and `-P` are mutually exclusive output destinations.
- `-r`/`-R` provide rsync-friendly level-0 dumps by suppressing volatile times.
- `-W`/`-w` delegate to `lastdump()`.

Important logic:
- `getmntpt()` scans mounted filesystems by source device.
- `numarg()` validates numeric option ranges.
- `sig()` rewrites the current volume on recoverable signals and aborts on `SIGSEGV`.
- `rawname()` now accepts only existing character devices.
- `obsolete()` transforms legacy clustered flags and positional arguments into normal `getopt()` form.

Risks and constraints:
- UFS-specific: expects UFS superblocks and UFS inode layout.
- Snapshot creation uses `system()` with constructed command strings and fixed `.snap/dump_snapshot` naming.
- Live read-write dumping without `-L` is permitted but warned as unsafe.
- Many globals couple this file tightly to `tape.c`, `traverse.c`, `itime.c`, and `optr.c`.
