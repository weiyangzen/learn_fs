# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_todr.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_todr.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements the kernel time-of-day register bridge for reading and writing hardware RTC/TOD clocks.

## Purpose And Main Interfaces

- Initialization and locking:
  - `todr_init`
  - `todr_lock`
  - `todr_unlock`
  - `todr_lock_owned`
- Device attachment:
  - `todr_attach`
- System time synchronization:
  - `todr_set_systime`
  - `todr_save_systime`
  - `inittodr`
  - `resettodr`
- Internal hardware operations:
  - `todr_gettime`
  - `todr_settime`

## Key Data Structures

- `todr_mutex` serializes TODR access.
- `todr_handle` stores the selected `todr_chip_handle_t`.
- `todr_initialized` catches early attachment misuse.
- `timeset` tracks whether system time has been established and should be saved back.
- `PREPOSTEROUS_YEARS` defines the minimum reasonable RTC year threshold, based on 2021.

## Control Flow

- `todr_attach` rejects non-system TODR devices if the backing device supports `DEVICE_IS_SYSTEM_TODR`, and only permits one configured TODR.
- `todr_set_systime` takes a filesystem-derived base time, rejects preposterous bases, reads the TODR if present, compares RTC and filesystem time, decides whether RTC or filesystem/default time is more trustworthy, seeds randomness with observed time data, and calls `tc_setclock`.
- If the RTC is absent or invalid, `todr_set_systime` logs warnings and uses filesystem/default base.
- `todr_save_systime` writes current kernel time back to the TODR only if system time was previously set and is nonzero.
- `resettodr` uses `mutex_tryenter` during shutdown to avoid hanging if another thread is using the RTC.
- `todr_gettime` supports either seconds-based or `clock_ymdhms` driver callbacks, enables TODR writes around operations if required by the device, applies `rtc_offset`, and validates calendar fields.
- `todr_settime` supports seconds-based or `clock_ymdhms` callbacks, subtracts `rtc_offset`, rounds microseconds for YMDHMS devices, and toggles write enable.

## Concurrency And Invariants

- Public time setting/saving functions require the TODR lock as documented and asserted.
- Driver callbacks can require write-enable even for reads.
- `todr_attach` asserts initialization has occurred.
- Only one global TODR handle is accepted.

## Risks And Edge Cases

- Bad RTC values before the 2021-derived threshold are rejected.
- Filesystem base time below five common years is treated as preposterous, except base zero suppresses one warning because it may mean unknown.
- RTC behind filesystem time by two or more days is treated as lost clock and rejected; RTC ahead is accepted with verbose warning.
- Shutdown writeback deliberately avoids blocking forever on `todr_mutex`.
