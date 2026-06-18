# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpudrv.h

## Role

Defines private CPU power-management driver state, speed-level data, monitoring thresholds, and driver/machine hooks.

## Speed State

- `cpudrv_pm_spd_t`:
  - platform-dependent `speed`.
  - monitoring quantum count.
  - up/down speed links.
  - idle and user high/low watermarks.
  - counters for hysteresis.
  - power framework level.

The comment notes speed means divisor on SPARC and frequency on x86.

## PM State

- `cpudrv_pm_t`:
  - speed list head/current speed and count.
  - last microstate accounting snapshot.
  - PM busy count.
  - taskq, timeout id/count/lock/cv.
  - x86-only governor thread and effective top speed.
  - `pm_started`.

## Thresholds and Timing

- x86 and non-x86 idle thresholds differ.
- `CPUDRV_USER_HWM`, `CPUDRV_IDLE_BUF_ZONE`.
- `CPUDRV_QUANT_CNT_NORMAL` is 1 second on x86, 5 seconds elsewhere.
- `CPUDRV_QUANT_CNT_OTHR` is 1 second.
- Taskq dimensions are fixed to one worker and small queue bounds.

## Driver State

- `cpudrv_devstate_t`: devinfo handle, CPU pointer/id, PM data, and lock.
- Globals:
  - `cpudrv_state`
  - `cpudrv_enabled`

## Debugging

Under `DEBUG`, defines debug categories and `DPRINTF()` backed by `prom_printf`.

## Function Surface

Declares speed change, CPU id lookup, governor-thread detection, machine init/fini, readiness/enabled checks, supported-frequency setup, and CPU lookup helpers.

## Research Relevance

Useful for understanding CPU frequency/power transitions and their interaction with dispatcher microstate accounting.
