# File Research: sources/os/bsd/netbsd-src/sys/sys/drvctlio.h

Defines the experimental `/dev/drvctl` user/kernel ioctl interface for device management.

Key content:
- Device path: `DRVCTLDEV`.
- Argument structs for detach, list children, power-management operations, and bus rescan.
- `DEVPM_F_SUBTREE` flag.
- Ioctls: detach device, rescan bus, generic plist command, resume, list, get event, suspend.
- Detailed documentation for `DRVCTLCOMMAND` request and response dictionaries.
- Documents `get-properties` command.

Important behavior:
- Uses proplib dictionaries through `plistref` for extensible commands.
- Interface is explicitly marked experimental.
