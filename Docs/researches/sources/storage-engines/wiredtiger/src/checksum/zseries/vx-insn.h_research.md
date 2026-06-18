# sources/storage-engines/wiredtiger/src/checksum/zseries/vx-insn.h

## Purpose
This assembler header provides macros for emitting s390x vector instructions manually. It exists so the CRC assembly can build with binutils versions that do not understand all vector mnemonics natively.

## Important APIs, Types, and Functions
`WT_CRC32_ENTRY(name)` emits a global aligned function label. `GR_NUM`, `VX_NUM`, `RXB`, `MRXB`, and `MRXBOPC` derive register numbers and opcode extension bits. Instruction macros include `VZERO`, `VLVGF`, `VL`, `VLM`, `VSTM`, `VPERM`, `VUPLLF`, `VX`, `VGFMG`, `VGFMAG`, `VSRLB`, and related element load/store helpers.

## Control Flow
The header is macro-only. Each macro validates textual register names where applicable, emits `.word` and `.byte` opcode fragments, and computes RXB fields for high vector registers. `crc32le-vx.S` expands these macros to build the folding and Barrett reduction kernel.

## State and Persistence
No runtime state exists. The generated instruction bytes become part of the executable text. Correct macro expansion is necessary for persistent checksum correctness because it determines the actual hardware operations used by the vector backend.

## Dependencies and Integration Points
The file is included by `crc32le-vx.S` and is guarded by `__ASM_S390_VX_INSN_H`. It depends on GNU assembler macro syntax. It is not a general C header despite the `.h` suffix.

## Risks and Edge Cases
Register-name parsing is explicit and easy to break when new register forms are introduced. Encoding bugs can compile successfully but execute the wrong instruction. This file is also toolchain-sensitive because it relies on assembler expression behavior and macro defaults.

## Test Signals
The key signals are successful s390x assembly builds across supported binutils versions and runtime CRC comparisons on VX-capable machines. Disassembly review is useful after macro changes because source-level tests may not isolate encoding regressions quickly.
