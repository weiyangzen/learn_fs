# File Research: sources/os/bsd/dragonflybsd/sys/sys/power.h

Power management type, command, sleep-state, and power-profile kernel API definitions.

Key responsibilities:
- Defines power management system types: APM, ACPI, and none.
- Defines suspend command and standby/suspend/hibernate sleep-state constants.
- Defines `power_pm_fn_t` callback type and kernel APIs to register a power manager, get type, and suspend.
- Defines performance/economy power profile constants and get/set APIs.
- Declares `power_profile_change` eventhandler hook.
- Provides inline `powerstate_to_str()` mapping numeric D-states to strings.

Important behavior:
- Kernel APIs are available only under `_KERNEL`, but `powerstate_to_str()` is outside that guard.
- `powerstate_to_str()` assumes `state` is a valid index 0-4.

Dependencies:
- Kernel section includes `types.h` and `eventhandler.h`.

Notable risks:
- `powerstate_to_str()` has no bounds check, so invalid states can read past the static string table.
- PM callback signature is variadic, requiring strict convention between caller and provider.
