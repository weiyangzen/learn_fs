# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotplug/hpcsvc.h

## Role

`hpcsvc.h` declares Hot Plug Services interfaces used by nexus drivers to interact with registered hot-plug controller slots.

## Key Interfaces and Data

- Includes `hpctrl.h` for slot handles, slot info, and operation definitions.
- Event handling flags:
  - `HPC_EVENT_NORMAL` for queued handling.
  - `HPC_EVENT_SYNCHRONOUS` for unqueued synchronous handling.
- Declares nexus bus register/unregister APIs with a callback receiving `dev_info_t`, slot handle, slot info, and slot state.
- Declares nexus operations for connect, disconnect, insert, remove, and control.
- Declares event handler install/remove APIs for a slot and event mask.

## Dependencies and Use

This is the service-facing counterpart to `hpctrl.h`; hot-plug controller drivers register slots, while nexus code uses these functions to manage and observe them.

## Research Notes

The interface preserves a clear split between hot-plug controller operations and nexus bus policy.
