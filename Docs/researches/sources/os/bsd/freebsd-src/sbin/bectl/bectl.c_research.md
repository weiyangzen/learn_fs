# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl.c

## Purpose
Main command dispatcher for `bectl`, implementing boot environment lifecycle commands backed by libbe.

## Main Elements
- `usage()`: prints all subcommands and options.
- `command_map`: maps command names to handlers, libbe error-printing behavior, and history logging policy.
- Command handlers:
  - `activate`: permanent, temporary next-boot, or temporary-activation reset.
  - `create`: creates BEs from active BE, named BE, snapshot, recursive clone, snapshot-only form, or empty BE.
  - `destroy`: supports force/origin flags and warns when non-auto origin snapshots are left intact.
  - `export` / `import`: stream BE data over stdout/stdin, rejecting terminal use.
  - `mount` / `unmount`: mount deeply, optionally at a caller-provided path, with force unmount.
  - `rename`: renames a BE.
  - `check`: silent initialization probe.
- `save_cmdline()`: builds a bounded history string for ZFS history logging.
- `main()`: parses global `-h` and `-r`, initializes libbe, dispatches command, logs successful mutating commands, and closes libbe.

## Dependencies And Integration
Uses `libbe`, `libutil`, nvlist properties, ZFS history logging, and helpers exported by `bectl_jail.c` and `bectl_list.c`.

## Risk Notes
Most commands mutate ZFS datasets or boot configuration. Import/export intentionally use raw file descriptors, so terminal checks are important safety gates.
