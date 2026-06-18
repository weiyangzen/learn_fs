# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtend.S

RISC-V section terminator object. It defines pointer-aligned hidden/global `__EH_FRAME_END__` and `__JCR_END__`.

Padding size is computed from `PTR_SCALESHIFT`, making it pointer-width aware.
