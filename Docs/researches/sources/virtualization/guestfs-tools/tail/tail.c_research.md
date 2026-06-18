# File Research: sources/virtualization/guestfs-tools/tail/tail.c

C implementation of `virt-tail`, a read-only tool that follows files inside a guest disk image.

Key behavior:
- Uses libguestfs and common option parsing helpers.
- Supports `-a`, `-d`, `-c`, `-m`, `--format`, `--blocksize`, `--key`, `--keys-from-stdin`, `--echo-keys`, `-v`, `-V`, `-x`, and `-f` compatibility.
- Forces `read_only = 1`; `-m` disables inspection and uses explicit mountpoints.
- Requires at least one disk/domain and at least one guest filename.
- Installs SIGINT/SIGQUIT handlers that set a quit flag and call `guestfs_user_cancel`.
- In the main loop, adds drives, optionally enables network for keys, launches guestfs, mounts via explicit mount list or inspection, and detects Windows guests for path conversion.
- Tracks each watched file’s last mtime and size.
- For missing files, treats `ENOENT` as empty; for other stat errors, fails.
- When a file changes:
  - prints a filename banner when switching displayed files,
  - if it grew slightly, reads only appended bytes via `guestfs_pread`,
  - if it grew a lot, shrank, or changed at same size, prints `guestfs_tail` output.
- Exits with an error if no watched files are found on the first pass.
- Exits successfully if all watched files disappear after a previous successful pass.
- Polls local disk mtimes with 30-second sleeps, up to roughly five minutes, and uses fixed delay behavior for libvirt/remote sources.
- Reopens the guestfs handle between polling cycles, carrying verbose, trace, and pgroup settings.

Research notes:
- Local disk change detection is based on host `stat` mtimes for `-a` drives only; libvirt/local-drive introspection is noted as future work.
- Windows paths are resolved through shared Windows helper support in read-only mode.
