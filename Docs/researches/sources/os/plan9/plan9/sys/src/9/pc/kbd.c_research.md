# File Research: sources/os/plan9/plan9/sys/src/9/pc/kbd.c

- Size/hash: 741 lines, 14969 bytes, SHA-256 `7841895089780d4f8199eb782dc59a7357b2c83331c91e98fe2c15e4cd8f41f5`.
- Purpose: i8042 PS/2 keyboard and auxiliary-port input driver, including scan-code translation tables and runtime keymap accessors.
- Data tables: Defines `kbtab`, `kbtabshift`, `kbtabesc1`, `kbtabaltgr`, and `kbtabctrl` for normal, shifted, escaped, AltGr, and control scan-code mappings.
- State: `Kbscan` tracks escape prefixes, modifier states, compose collection, mouse-button state, and collected runes separately for internal and external scan sources.
- Controller helpers: `outready` and `inready` poll status bits; `i8042a20` enables A20; `i8042reset` requests reset through the keyboard controller.
- Aux path: `i8042auxcmd`, `i8042auxcmds`, and `i8042auxenable` send mouse/aux commands through command `0xD4`, install an aux byte callback, and enable `IrqAUX`.
- Keyboard path: `kbdinit` drains and configures the controller command byte; `kbdenable` allocates `kbdq`, claims I/O ports, enables `IrqKBD`, and clears num-lock LED state.
- Interrupt flow: `i8042intr` reads status/data under lock, dispatches mouse bytes if `Minready` is set, otherwise passes keyboard scan codes to `kbdputsc`.
- Translation flow: `kbdputsc` handles E0/E1 escapes, key-up state, modifiers, compose sequences via `latin1`, Ctrl-Alt-Del exit, F11/F12 debug toggles, and queueing translated runes to `kbdq`.
- Keymap API: `kbdputmap` and `kbdgetmap` expose editable mapping tables used by the generic keyboard-map device.
- Dependencies: Uses `inb/outb`, `delay`, `intrenable`, `kbdputc`, `kbdq`, `latin1`, `qopen`, `qnoblock`, Plan 9 error handling, and `io.h` IRQ constants.
- Research notes: Not filesystem code, but part of the PC console/input substrate used during local boot, configuration, and interactive recovery.
