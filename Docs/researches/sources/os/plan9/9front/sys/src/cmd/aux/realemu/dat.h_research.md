# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/dat.h

`dat.h` defines the real-mode emulator’s core data model: register indices, `Iarg`, decoded `Inst`, `Bus`, `Cpu`, `Pcidev`, and `Pit`.

It enumerates processor flags, trap/interrupt numbers, operand tags and operand descriptor kinds, and every supported opcode class (`OADD`, `OMOV`, `OJUMP`, etc.). `Cpu` includes general/segment registers, instruction count, memory and port buses, trap state, default operand/address/stack widths, jump buffer, and operand scratch buffer.

The header frames the emulator as a 16/32-bit-capable x86 decoder/executor with segmented real-mode addressing over pluggable memory and I/O buses.
