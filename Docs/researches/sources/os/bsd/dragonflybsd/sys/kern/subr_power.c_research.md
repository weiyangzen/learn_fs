# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_power.c

## Summary
Provides a minimal power-management callback registry and power-profile state notification.

## Main Responsibilities
- `power_pm_register()` installs a power-management backend callback for one PM type.
- `power_pm_get_type()` reports the registered PM type.
- `power_pm_suspend()` validates standby/suspend/hibernate requests and calls the backend.
- `power_profile_get_state()` / `power_profile_set_state()` manage performance/economy profile state.
- Emits `power_profile_change` eventhandler notifications on profile changes.

## Important Behavior
Only one PM type is accepted unless the existing type matches. Suspend requests are ignored if no backend is registered or if the sleep state is unsupported.

## Risks
There is no locking around global PM/profile state. Profile logging assumes only known profile constants, printing non-performance as `economy`.
