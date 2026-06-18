# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/gc.h

This is the amd64 backend header for `6c`. It includes generic C compiler definitions and amd64 object definitions, then declares target sizes, backend data structures, globals, macros, and function prototypes.

Core structures include `Adr` for machine operands, `Prog` for emitted instructions, `Case`/`C1` for switch lowering, `Var` for register allocation candidates, `Reg` for control-flow/liveness nodes, `Rgn` for register allocation regions, and `Renv` for register environment state.

The header defines target sizes: 8-byte pointers, 4-byte long/int, 8-byte vlong/double, and amd64-specific return/register roles. It declares global compiler backend state such as instruction lists, string data buffers, register arrays, live-variable bitsets, region arrays, and external register offsets.

It also prototypes the full backend: statement generation, expression generation, object output, switch lowering, register allocation, peephole optimization, 64-bit support hooks, division/multiplication lowering, and formatted listing.

Filesystem relevance is as target ABI/build infrastructure. It controls how Plan 9 amd64 C code, including filesystem and kernel code, is represented before assembly/linking.
