# File Research: sources/os/plan9/plan9/sys/src/9/ppc/lucu.h

Assembly fragment defining a UCU-specific `mmuinit0` for PPC 755/Saturn-style startup.

Key responsibilities:
- Clears 64 TLB entries.
- Maps `KZERO` to physical 0 using BAT2 only, for a 256 MiB kernel DRAM window.
- Enables instruction/data MMU, recoverable exceptions, and FP through SRR0/SRR1 plus `RFI`.

Dependencies:
- Uses `mem.h` PowerPC/BAT constants and assembler macros.
- Mirrors the `ucuconf` `mmuinit0` branch embedded in `l.s`.

Notable risks:
- Legacy/include-style duplicate of code now present in `l.s`.
- BAT2-only setup is board-specific and relies on later `ucuconf` code copying BAT2 into other BAT slots.
