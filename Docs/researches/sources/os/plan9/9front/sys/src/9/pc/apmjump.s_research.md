# File Research: sources/os/plan9/9front/sys/src/9/pc/apmjump.s

Assembly helper for non-reentrant absolute far calls into the APM BIOS.

Key responsibilities:
- Implements `apmfarcall(seg, off, ureg)` for `apm.c`.
- Loads AX/BX/CX/DX from the supplied `Ureg`, saves data segment registers and selected general registers, and performs an indirect far call through `apmjumpstruct`.
- Clears DS/ES/FS/GS before the BIOS call so the BIOS must initialize segment state itself.
- Stores carry flag and selected result registers back into the `Ureg`.

Important behavior:
- Uses a global 8-byte jump structure, so calls are explicitly not reentrant or thread-safe.
- Returns the carry flag as the function result.
- Writes flags to the `Ureg` flags slot and updates AX/BX/CX/DX/SI.

Dependencies:
- Depends on Plan 9 x86 assembler conventions, `mem.h` segment definitions, and the `Ureg` layout expected by `apm.c`.

Notable risks:
- Correctness depends on hard-coded `Ureg` offsets.
- Segment-register and stack manipulation means the function cannot safely use normal frame-pointer access after its first push/pop.
