# File Research: sources/os/bsd/netbsd-src/sys/sys/userconf.h

Read completely: 39 lines.

Declares kernel user configuration prompt hooks.

Key elements:
- Includes `sys/cpu.h`.
- Declares `userconf_bootinfo()`, `userconf_init()`, `userconf_prompt()`, and `userconf_parse(char *)`.

Risks and notes:
- Interface is small but boot/configuration-path sensitive.
- Parsing behavior lives outside the header.
