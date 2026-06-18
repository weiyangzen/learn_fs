# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdk.h

## Scope

Complete file read, 103 lines. This header defines the common disk driver soft-state structure used by the `cmdk` layer.

## Public Surface

The header includes `sys/cmlb.h` and `sys/dktp/tgdk.h`. It defines:

- `CMDK_UNITSHF` and `CMDK_MAXPART` for minor-number partition packing.
- `CMDK_HWIDLEN`.
- `struct cmdk`: per-device state including devinfo, device number, target disk object, CMLB handle, device id, open state, bad-block handling data, alternate-sector data, and power-management fields.
- Power states `CMDK_SPINDLE_UNINIT`, `CMDK_SPINDLE_OFF`, `CMDK_SPINDLE_ON`.
- Driver flags `CMDK_OPEN`, `CMDK_SUSPEND`, `CMDK_TGDK_OPEN`.
- `CMDKUNIT(dev)` and `CMDKPART(dev)` minor decoding macros.

## Behavior And Integration

`struct cmdk` ties the common disk label/block layer (`cmlb`) to the target disk abstraction (`tgdk`) and bad-block handler (`bbh`). It records per-partition opens with bitmaps and layer counts, supports alternate-sector remap state, and tracks PM suspend/spindle state.

## Dependencies And Invariants

The minor layout reserves 6 low bits for partition number, yielding 64 partitions. `dk_open_reg` and `dk_open_exl` are `uint64_t`, matching that partition count. Alternate-sector fields are protected by `dk_bbh_mutex`; PM fields use `dk_pm_mutex` and `dk_suspend_cv`.

## Risks

Changing `CMDK_UNITSHF` changes device minor ABI interpretation. The structure embeds multiple synchronization domains; callers must use the documented locks around BBH and PM fields. Open bitmaps assume partition numbers are below `CMDK_MAXPART`.
