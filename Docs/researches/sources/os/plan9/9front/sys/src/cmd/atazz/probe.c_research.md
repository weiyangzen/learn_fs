# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/probe.c

Device discovery helper for `atazz`.

Important behavior:
- Reads `/dev/sdctl` to discover storage controller prefixes.
- Tries `/dev/<prefix><n>` paths for units 0-9.
- Uses `opendev` with squelched error output to identify ATA-compatible devices.
- Prints device path, sector count, sector size, and WWN.

This is a convenience probe layer over the main open/identify path.
