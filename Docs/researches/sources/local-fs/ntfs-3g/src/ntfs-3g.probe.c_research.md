# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.c

## Role

`ntfs-3g.probe.c` implements the `ntfs-3g.probe` command-line utility. It tests whether a device or image can be mounted by libntfs-3g in read-only or read-write mode and exits with a standardized NTFS-3G volume status code.

## Data Model

- `probe_t` has three states: unset, read-only probe, and read-write probe.
- The static `opts` struct stores the selected probe type and copied device path.
- `EXEC_NAME` is `ntfs-3g.probe` for logging and usage output.

## Control Flow

1. `main()` directs NTFS logging to stderr.
2. `parse_options()` parses command-line arguments.
3. On parse failure, `usage()` is printed and the process exits with `NTFS_VOLUME_SYNTAX_ERROR`.
4. `ntfs_open()` attempts to mount the selected device.
5. If mount succeeds, it immediately unmounts.
6. The program exits with the returned volume status, or `0` on success.

## Option Parsing

`parse_options()` uses `getopt_long()` with:

- `-r`, `--readonly`
- `-w`, `--readwrite`
- `-h`, `--help`
- one non-option device argument

Behavior:

- The first non-option argument is copied into a `PATH_MAX + 1` buffer allocated by `ntfs_malloc()`.
- A second device argument is rejected.
- Missing device is rejected.
- Missing probe type is rejected.
- Unknown options are reported with the original option spelling.
- `--help` prints usage and exits successfully.

One subtle point: if both `--readonly` and `--readwrite` are supplied, the later option wins; the parser only rejects missing probe type, not conflicting repeated modes.

## Mount Probe Semantics

`ntfs_open()`:

- Sets `NTFS_MNT_RDONLY` only for read-only probe mode.
- Calls `ntfs_mount(device, flags)`.
- Converts mount failure `errno` with `ntfs_volume_error(errno)`.
- If mounting succeeds, calls `ntfs_umount(vol, FALSE)`.
- Converts unmount failure `errno` the same way.
- Returns `NTFS_VOLUME_OK` on full success.

The read-write probe does not set special recovery, hibernation, or FUSE flags; it directly tests libntfs mountability.

## Important Dependencies

- `volume.h` for `ntfs_mount()`, `ntfs_umount()`, and `NTFS_VOLUME_*` status handling.
- `misc.h` for `ntfs_volume_error()`, `ntfs_home`, and allocation helpers.
- `compat.h` and generated `config.h` for portability.
- libc `getopt_long()` for CLI parsing.

## Notable Limitations And Risk Areas

- This utility probes libntfs mountability only; it does not mount through FUSE or validate FUSE availability.
- Read-write probe behavior depends on libntfs mount checks and current volume state such as dirty, hibernated, locked, or invalid NTFS.
- Conflicting `--readonly` and `--readwrite` options are accepted with last-one-wins behavior.
- Device names longer than `PATH_MAX` are truncated by `strncpy()` into the fixed buffer.
