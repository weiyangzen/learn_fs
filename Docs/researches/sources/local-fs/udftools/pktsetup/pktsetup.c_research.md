# File Research: sources/local-fs/udftools/pktsetup/pktsetup.c

## Role

User-space pktcdvd mapping manager. It sets up, tears down, and lists packet-writing block-device associations.

## Main Responsibilities

- Supports legacy pktcdvd ioctls on packet block device paths.
- Supports newer pktcdvd control character device API via `/dev/pktcdvd/control`.
- Creates the pktcdvd control node when needed by locating `/proc/misc` entry and loading `pktcdvd` with `/sbin/modprobe` if absent.
- Creates/removes packet block device nodes under `/dev/pktcdvd`.
- Supports idempotent behavior with `-i`.
- Lists active mappings with `-s`.

## Important Functions

- `init_cdrom()` probes drive and disc status to force TOC read and reject not-ready/no-disc cases.
- `setup_dev()` implements old API using `PACKET_SETUP_DEV` and `PACKET_TEARDOWN_DEV` ioctls.
- `get_misc_minor()` finds the pktcdvd misc minor in `/proc/misc`.
- `create_ctl_dev()` ensures `/dev/pktcdvd/control` exists and matches the pktcdvd misc device.
- `remove_stale_dev_node()` removes stale block nodes if no active mapping owns them.
- `find_pkdev_for_dev()` maps an underlying block dev to an existing pktcdvd dev via status ioctl.
- `setup_dev_chardev()` handles setup/teardown through `PACKET_CTRL_CMD`.
- `show_mappings()` prints active mapping index and major/minor pairs.
- `main()` parses `-d`, `-i`, `-s`, detects old API by slash-containing pkt device argument, and dispatches.

## Dependencies

- Linux CD-ROM and pktcdvd ioctl ABI.
- `/proc/misc`, `/dev/pktcdvd`, `mknod`, and root-like permissions for node management.

## Notable Behaviors

- `-i` suppresses errors for already-existing mappings or missing teardown targets.
- Teardown can accept either pkt device name or `major:minor`.
- If direct teardown by packet dev fails with `ENXIO`, it tries interpreting the supplied major/minor as the backing device and searches the mapping table.
- Stale custom device nodes are removed; default `pktcdvd*` nodes are preserved.

## Research Notes

This is Linux-specific device-management code. Any modernization should preserve both control-device API and legacy API behavior unless old kernel support is intentionally dropped.
