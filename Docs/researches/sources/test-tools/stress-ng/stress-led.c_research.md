# sources/test-tools/stress-ng/stress-led.c

Purpose: implements `led`, a Linux sysfs LED stressor that enumerates `/sys/class/leds`, cycles trigger settings, sweeps brightness values, and restores original LED state.

Important APIs/types/functions: `stress_led_info_t` stores path, device name, original trigger, trigger list, original brightness, max brightness, and linked-list pointer. `stress_led_info_get()` discovers LED entries and captures state. `stress_led_exercise()` tokenizes trigger options and writes trigger/brightness files. `stress_led_info_free()` restores and frees the list.

Control flow: the worker reports lack of root privilege as informational, sync-starts, builds a randomized list of LED devices, and skips if none are usable. The loop walks each LED, sets each trigger token after removing bracket markers, sweeps brightness from zero to max in up to 16 steps, restores original brightness and trigger, increments bogo ops, and repeats until stopped.

State and persistence behavior: the stressor intentionally mutates sysfs LED trigger and brightness attributes, then restores captured values both after each LED exercise and during final free. State may persist visually or in sysfs if the process is killed outside normal cleanup.

Dependencies and integration points: Linux-only. Uses stress-ng file read/write helpers, dirent cleanup, random shuffling, capability check, and process state. Registered as `CLASS_OS`.

Risks: writing LED sysfs attributes can visibly alter hardware indicators. Not all triggers accept writes, and non-root runs may mostly read state. `orig_trigger` parsing depends on kernel bracket formatting.

Test signals: run on systems with no LEDs, read-only LEDs, and writable LEDs; verify original brightness/trigger restoration, no leaked list nodes, and no failure when individual LED entries lack expected files.
