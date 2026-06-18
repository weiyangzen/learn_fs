# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/616

## Purpose
This fixture validates an arm64 tag-based KASAN invalid read attributed to `ip6_mc_del1_src`.

## Important APIs, types, and functions
Important frames include `__list_add_valid`, `ip6_mc_del1_src`, `firmware_fallback_sysfs`, `_request_firmware`, `request_firmware`, `devlink_compat_flash_update`, `ethtool_flash_device`, `dev_ethtool`, `dev_ioctl`, `sock_ioctl`, and `__arm64_sys_ioctl`.

## Control flow
An ioctl path invokes ethtool flash update, requests firmware, and hits a tag mismatch while list manipulation occurs. The log includes allocation and free stacks for the same kmalloc object.

## State and persistence behavior
The file persists KASAN object lifetime evidence: pointer tag, memory tag, allocation stack, free stack, object cache, and memory state bytes.

## Dependencies and integration points
It exercises syzkaller parsing for arm64 KASAN tag-check faults, firmware fallback, devlink compatibility, ethtool, and IPv6 multicast symbol attribution.

## Risks and test signals
The title should use `KASAN: invalid-access Read in ip6_mc_del1_src` even though the first bad access frame is `__list_add_valid`. `TYPE: KASAN-READ` is the expected type.
