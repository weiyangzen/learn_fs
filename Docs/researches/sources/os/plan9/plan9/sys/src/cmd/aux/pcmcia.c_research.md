# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/pcmcia.c

PCMCIA Card Information Structure tuple decoder. It reads attribute memory, decodes known CIS tuples, and prints human-readable information about devices, version strings, function IDs, configuration registers, power, timing, I/O ranges, IRQs, and memory ranges.

Core behavior:
- Defaults to reading `#y/pcm0attr`; optional file argument overrides it.
- Attribute memory is read with `seek(fd, 2*pos, 0)`, matching PCMCIA attribute-space byte layout.
- `-x` prints raw hex bytes as they are read.
- Tuple dispatch is through `parse[256]`.

Supported tuple handlers:
- Device tuples: `tdevice()`.
- Multifunction long links: `tlonglnkmfc()`.
- Version 1 strings: `tvers1()`.
- Config registers: `tcfig()`.
- Config entries: `tentry()`.
- Function ID: `tfuncid()`.

Dependencies and integration:
- Standalone Plan 9 command using libc only.
- Primarily diagnostic/inspection tooling, not a driver.

Notable risks:
- Many decoder routines trust tuple lengths and stream structure; malformed CIS data may desynchronize parsing.
- `tuple()` always prints the tuple type, even without `-x`, so output is inherently verbose.
- The multifunction recursion follows linked tuple chains without a global visited-set.
