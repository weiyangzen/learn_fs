# File Research: sources/os/plan9/9front/sys/src/9/pc/bootargs.c

Boot configuration parser and multiboot-to-Plan-9 argument converter.

Key responsibilities:
- Converts multiboot memory maps into `*e820=` lines.
- Converts multiboot framebuffer or VBE information into `*bootscreen=` configuration.
- Imports first multiboot module contents as `plan9.ini` text and appends multiboot command-line tokens.
- Normalizes CR/TAB characters, parses `name=value` configuration lines, and stores case-insensitive configuration keys.
- Exposes `getconf()`, `setconfenv()`, and `writeconf()` for kernel configuration consumers.

Important behavior:
- Later duplicate configuration lines overwrite earlier values for the same case-insensitive name.
- Environment setup stores non-star names as normal environment variables and all names as configuration variables.
- `writeconf()` converts current kernel environment back into `BOOTARGS` format and clears `BOOTLINE`.

Dependencies:
- Depends on boot memory constants, multiboot pointer, VESA/screen helpers, tokenization, and kernel environment helpers.

Notable risks:
- Uses fixed `MAXCONF` and `BOOTARGSLEN` capacities.
- Multiboot pointer is ignored if it is zero or above `MemMin`.
