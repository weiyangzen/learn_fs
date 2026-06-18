# sources/storage-engines/wiredtiger/cmake/platform/arch/riscv64.cmake

## Purpose
`riscv64.cmake` sets the baseline RISC-V 64-bit compiler ABI and ISA flags for WiredTiger.

## Important APIs, Types, And Functions
It contains a single `add_compile_options(-march=rv64imafdc -mabi=lp64d)` call.

## Control Flow
There is no branching. All selected riscv64 builds receive the same ISA/ABI options.

## State And Persistence Behavior
It mutates global compile options in the build directory.

## Dependencies And Integration Points
It is selected by architecture platform setup and depends on a compiler accepting `rv64imafdc` and `lp64d`.

## Risks
The hard-coded ISA/ABI may not match every RISC-V target, particularly reduced-extension or different ABI environments.

## Test Signals
Configure and compile with the intended RISC-V toolchain; verify emitted flags and ABI compatibility with linked libraries.
