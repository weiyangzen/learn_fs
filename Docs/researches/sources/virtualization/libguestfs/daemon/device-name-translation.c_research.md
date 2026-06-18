# File Research: sources/virtualization/libguestfs/daemon/device-name-translation.c

Implements stable public device-name translation for daemon block device paths.

Key points:
- At startup, `device_name_translation_init` caches non-partition `/dev/disk/by-path` symlinks, sorted by `ls -1v`, excluding the root appliance device.
- Translates public `/dev/sdX`, `/dev/hdX`, and `/dev/vdX`-style names to actual kernel device names using drive index mapping.
- Leaves MD, LVM, mapper, and dm paths untranslated.
- Verifies translated devices are openable; falls back from `/dev/sd*` to `/dev/vd*`, `/dev/hd*`, and `/dev/ubd*` variants when needed.
- `reverse_device_name_translation` maps cached real devices back to canonical `/dev/sdX` names.
- Also reverses `btrfsvol:/dev/.../subvol` descriptors.
