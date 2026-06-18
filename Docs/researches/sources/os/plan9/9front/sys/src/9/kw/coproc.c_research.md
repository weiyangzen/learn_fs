# File Research: sources/os/plan9/9front/sys/src/9/kw/coproc.c

Implements dynamic ARM coprocessor and VFP register access helpers.

Key elements:
- Builds small instruction stubs at runtime for MCR/MRC coprocessor writes/reads.
- Maps the stub into the caller’s PC space, writes back data cache, invalidates instruction cache, and calls it.
- Provides CP15 wrappers `cpwrsc` and `cprdsc`.
- Provides VFP register read/write helpers `fprd` and `fpwr`.

Dependencies:
- Uses ARM instruction encodings, cache maintenance helpers, interrupt masking, and `arm.h` constants.

Research notes:
- Dynamic instruction generation avoids needing one assembly routine per coprocessor register encoding.
- The code runs with interrupts raised while patching/executing the stub.
