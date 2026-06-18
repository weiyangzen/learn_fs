# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm_x86.c

This is the x86 helper/emulation layer for NetBSD's NVMM userland library. It provides `nvmm_vcpu_dump`, guest virtual-to-physical translation, I/O exit assistance, and memory exit instruction decoding/emulation.

The address translation path handles non-paged, 32-bit, 32-bit PAE, and 64-bit paging. It walks guest page tables through `nvmm_gpa_to_hva`, tracks read/write/execute/user permissions, handles large pages where supported, and rejects noncanonical 64-bit addresses.

The I/O assistant handles `NVMM_VCPU_EXIT_IO`, including string I/O, segment-base application, direction-flag updates, REP counts, and batched non-decrementing string output/input via the VCPU I/O callback. The memory assistant fetches instruction bytes when the kernel did not provide them, decodes a supported subset of x86, and advances RIP or REP state after emulation.

The embedded decoder supports legacy prefixes, REX prefixes, ModRM/SIB/displacements, direct memory offsets, MOVS/CMPS/STOS/LODS, MOV/MOVZX/XCHG, OR/AND/SUB/XOR/CMP/TEST, and Group 1/3/11 opcodes. Arithmetic flag behavior is delegated to inline assembly helpers so emulation updates x86 flags consistently.

Important coupling: callbacks in `struct nvmm_vcpu::cbs` are required for MMIO and port I/O. Instruction support is intentionally partial; unsupported memory exits return `ENODEV`.
