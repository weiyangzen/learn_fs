# File Research: sources/os/plan9/plan9/sys/src/9/pc/apm.c

Advanced Power Management BIOS interface exposed through the PC arch device.

Key responsibilities:
- Parses APM register values from `plan9.ini` ISA configuration `apm0`.
- Builds three GDT descriptors required by the APM BIOS: 32-bit code, 16-bit code, and data.
- Adds `#P/apm` arch file for reading/writing a `Ureg`.
- `apmwrite` copies a user-provided `Ureg`, raises priority, calls BIOS through `apmfarcall`, then stores returned register state.
- `apmread` returns the last `Ureg` contents.

Important behavior:
- Forces both APM code segment lengths to 64 KiB due to a documented NEC Versa SX BIOS issue.
- Uses `KADDR(base)` when programming descriptors, meaning BIOS physical base addresses are mapped into kernel virtual space first.
- Prints configured APM code base and offset.

Dependencies:
- Depends on `apmfarcall` from `apmjump.s`, GDT layout in `Mach`, ISA configuration parsing, and `addarchfile`.

Notable risks:
- Comments call this a BIOS hack; it is tightly coupled to protected-mode descriptor details.
- The arch file write requires exactly a `Ureg` size.
