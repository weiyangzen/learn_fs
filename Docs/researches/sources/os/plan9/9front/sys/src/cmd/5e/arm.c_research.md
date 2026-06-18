# File Research: sources/os/plan9/9front/sys/src/cmd/5e/arm.c

This file implements ARM instruction fetch/decode/execute for `5e`.

Instruction support:
- `invalid()` and `evenaddr()` report undefined instructions and alignment faults.
- `doshift()` implements ARM shifter operand decoding for immediate/register shifts, logical/arithmetic shifts, rotate, and rotate-through-carry.
- `single()` handles single word/byte load/store with immediate or register-shift offset, pre/post indexing, writeback, PC-relative behavior, and segment locking.
- `swap()` emulates `SWP`/`SWPB` with host `cas()`.
- `add()` computes add/subtract with carry and overflow.
- `alu()` executes ARM data-processing ops, updates CPSR for S-bit ops, blocks unsupported PSR transfers, and handles PC operand quirks.
- `branch()` implements branch/link.
- `halfword()` handles halfword and signed byte/halfword load/store.
- `block()` handles block load/store without R15.
- `multiply()` and `multiplylong()` implement multiply, multiply-accumulate, and long signed/unsigned multiply variants.
- `singleex()` emulates `LDREX`/`STREX` with a per-process linked-load address/value approximation.
- `clrex()` clears exclusive state.
- `barrier()` provides a host lock/unlock memory barrier approximation.

Decode loop:
- `step()` fetches one instruction, advances PC, checks ARM condition codes, handles unconditional `CLREX`/barriers, and dispatches to swap, exclusive, multiply, load/store, halfword, ALU, branch, syscall, block transfer, FPA, or VFP handlers.

Dependencies and interactions:
- Uses `P->R`, `P->CPSR`, `vaddr()`, `segunlock()`, `syscall()`, FPA/VFP helpers, and emulator fault handling.
- Reads instructions from emulated memory segments.

Research relevance:
- Core CPU emulator for running ARM Plan 9 binaries on the host.

Risk notes:
- Exclusive-store emulation only checks whether the memory value changed from the linked value, not whether another core modified and restored it.
- Some instruction classes are intentionally unsupported and call `invalid()`/`sysfatal()`.
- `multiplylong()` flag handling appears unusual: it sets `flN` on zero and `flV` on high sign, reflecting historical emulator behavior rather than normal ARM NZ flags.
