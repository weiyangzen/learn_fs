# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_userconf.c

Read completely: 824 lines.

This file implements the interactive boot-time `userconf` configurator for kernel autoconfiguration data. It lets an operator list configured devices, find devices by name/unit, change locator values, enable/disable devices, set numeric display base, and control pagination.

Main state: static buffers track command input, additional prompts, history text, numeric base, device count, and pagination line count. The code operates directly on the global `cfdata[]` table and uses `cfiattr_lookup` for locator descriptions.

Key functions:
- `userconf_init` counts `cfdata` entries and calls `userconf_bootinfo`.
- `userconf_pdev` prints one device's name, parent attachment, disabled state, and locators.
- `userconf_number` parses decimal/octal/hex signed integers.
- `userconf_device` parses names like `sd0` or `sd*`.
- `userconf_change` prompts for locator edits and records history.
- `userconf_disable`/`userconf_enable` mutate `cf_fstate` between enabled and disabled states.
- `userconf_common_dev` applies find/change/enable/disable operations to all matching devices.
- `userconf_parse` dispatches commands and arguments.
- `userconf_prompt` runs the `uc> ` loop until quit.

Integration: this runs on the console using `cngetsn`, `cngetc`, and `cnpollc`, before or during autoconfiguration. It is intentionally simple and global-state driven.

Reliability notes: command buffers are fixed at 40 bytes and history is fixed at 1024 bytes; input APIs bound writes. Numeric parsing has limited overflow handling and uses `u_int`. One notable source-level oddity: `userconf_enable` records `userconf_hist_cmd('d')` when enabling, which appears inconsistent with the enable command and may affect replay/history text.
