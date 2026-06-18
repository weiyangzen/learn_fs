# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtend.S

PowerPC section terminator object. It emits pointer-width zero sentinels for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

The code handles 32-bit and 64-bit PowerPC with `.long` versus `.quad`.
