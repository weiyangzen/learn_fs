# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pshot.h

## Role

`pshot.h` is the private header for the `pshot` pseudo hotplug test driver. It defines user-visible node/property names plus kernel-only soft-state, minor-node, child-device, event, hotplug, power, bus, and debug interfaces.

## Public Surface

The user-accessible constants describe a small device topology:
- Two minor nodes per instance: `devctl` and `testctl`.
- Properties: `dev-name`, `dev-nt`, `dev-compat`.
- Minor-node limits: `PSHOT_MAX_MINOR_PERINST` and `PSHOT_MAX_MINOR_NAMELEN`.

## Kernel Structures

`pshot_minor_t` records a minor node’s owning `pshot_t`, minor number, and name. `pshot_t` carries:
- Instance, `dev_info_t`, lock, state bits.
- NDI event handle/set.
- interrupt block cookie.
- callback caches for normal and test callbacks.
- minor node array.
- power level and busy counters.

The state flags cover open/exclusive-open state, reset pending state, power/fail-suspend behavior, strict-parent/no-involuntary behavior, and power-management support.

## Event and Bus Interfaces

The header declares static prototypes for:
- Driver entry points: open, close, ioctl, probe, attach, detach, info, power.
- `devctl` and `testctl` ioctl handlers.
- Event names/tags for device offline/reset, bus reset/quiesce/unquiesce, debug, sub-reset, and test post.
- NDI event bus ops: get cookie, add/remove callback, post event.
- Bus config/unconfig, child init/uninit, control ops, interrupt ops, power setup, and property helpers.

## Research Notes

This header is effectively a complete private declaration block for a synthetic DDI/hotplug exerciser. It is useful for studying illumos device-tree event plumbing, minor encoding, and test-driver power/hotplug behavior rather than production storage or filesystem paths.
