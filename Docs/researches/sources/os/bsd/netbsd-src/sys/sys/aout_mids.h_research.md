# File Research: sources/os/bsd/netbsd-src/sys/sys/aout_mids.h

Read completely: 80 lines.

Defines machine ID constants for legacy a.out binaries and kernel core files.

Key elements:
- Machine IDs are kept in numerical order and are expected to satisfy `0 < mid < 0x3ff`, except `MID_ZERO`.
- Includes legacy Sun, PC/i386, m68k, ns32532, sparc, pmax, vax, alpha, MIPS, ARM6, SH3/SH5, PowerPC, m88k, HPPA, x86_64, IA64, AArch64, OpenRISC, RISC-V, hp200/hp300, and HP-UX IDs.
- Notes these IDs are still used in kernel core files.

Risks and notes:
- This is compatibility namespace; reusing or renumbering values would affect a.out/core interpretation.
