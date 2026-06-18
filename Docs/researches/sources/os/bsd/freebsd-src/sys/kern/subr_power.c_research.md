# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_power.c

## Purpose
Provides generic power-management device/sysctl glue and a global power profile notification mechanism.

## Main Interfaces
- Character device `/dev/power` with `power_ioctl()`, supporting `PIOTRANSITION`.
- Sleep type conversion: `power_name_to_stype()`, `power_stype_to_name()`.
- Provider registration: `power_pm_register()`, `power_pm_get_type()`.
- Transition request: `power_pm_suspend()`.
- Profile state: `power_profile_get_state()`, `power_profile_set_state()`.

## Implementation Notes
`power_init()` creates `/dev/power` owned by root/operator mode 0660. The ioctl path requires write permission and accepts a `uint32_t` transition value, checks enum overflow, then calls `power_pm_suspend()`.

`power_pm_register()` installs one provider type unless the same type is already registered, records supported sleep types, and picks default standby/suspend/hibernate stypes based on provider capabilities. Actual suspend is deferred through `taskqueue_thread`; `power_pm_deferred_fn()` invokes the provider callback with `POWER_CMD_SUSPEND`.

Sysctls expose supported sleep types and allow standby/suspend/hibernate type selection by string, rejecting unknown or unsupported values.

`power_profile_set_state()` updates global performance/economy state and invokes the `power_profile_change` eventhandler on changes.

## Dependencies
Uses character devices, sysctl, `taskqueue_thread`, eventhandlers, power enums/names, and credential/device creation APIs.

## Research Notes
This is OS power infrastructure. Filesystem relevance is indirect: suspend/hibernate transitions and power-profile changes affect storage quiescing and background work policy elsewhere.
