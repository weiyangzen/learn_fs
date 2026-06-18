# File Research: sources/local-fs/dosfstools/src/device_info.h

Public model and declarations for mkfs-side target-device analysis.

Contents:
- `enum device_type`:
  - `TYPE_UNKNOWN`
  - `TYPE_BAD`
  - `TYPE_FILE`
  - `TYPE_VIRTUAL`
  - `TYPE_REMOVABLE`
  - `TYPE_FIXED`
- `struct device_info` fields:
  - device type
  - partition number
  - child-device presence
  - geometry heads/sectors/start/size
  - sector size
  - byte size
- Declares `device_info_verbose`, `get_device_info()`, and `is_device_mounted()`.

Role:
- Provides mkfs with enough target information to choose geometry defaults and warn about unsafe targets.
