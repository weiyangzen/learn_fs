# File Research: sources/os/bsd/netbsd-src/sys/sys/power.h

## Purpose
Defines user/kernel power management event ABI for power switches, envsys sensor events, and power device ioctls.

## Main API
- Power switch types: `PSWITCH_TYPE_POWER`, `SLEEP`, `LID`, `RESET`, `ACADAPTER`, `HOTKEY`, `RADIO`.
- Hotkey names: display cycle, lock screen, battery info, eject, zoom, vendor, and ThinkPad-style function keys unless suppressed.
- Switch events: `PSWITCH_EVENT_PRESSED`, `PSWITCH_EVENT_RELEASED`.
- Structures: `struct pswitch_state`, `struct penvsys_state`, `power_event_t`, `struct power_type`.
- Envsys types/events: temperature, voltage, power, battery, fan, drive, indicator; normal, critical, warning, battery, low-power, state-changed, limits/capacity, null events.
- Ioctls: `POWER_EVENT_RECVDICT`, `POWER_IOC_GET_TYPE`.

## Dependencies
Uses `sys/ioccom.h`; userland includes `stdint.h`.

## Risks and Notes
Power event messages are fixed at 32 bytes so userland can read one event at a time. Kernel compatibility defines the older incorrectly encoded `POWER_IOC_GET_TYPE_WITH_LOSSAGE`.
