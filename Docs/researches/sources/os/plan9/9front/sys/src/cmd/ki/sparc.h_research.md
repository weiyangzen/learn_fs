# File Research: sources/os/plan9/9front/sys/src/cmd/ki/sparc.h

Central simulator header for `ki`. It defines SPARC user-address constants, breakpoint types, instruction categories, instruction-cache metadata, decoded instruction descriptors, CPU register state, memory segment structures, syscall/memory IO directions, and Plan 9 stack/text constants.

It declares all simulator, debugger, memory, syscall, breakpoint, profiling, and symbol-trace functions, plus global state such as `reg`, `memory`, `bplist`, `icache`, `iprof`, `symmap`, and tracing flags. Macros decode SPARC operand fields, sign-extend immediates, define PSR condition bits, and name FP compare outcomes. The header also documents portability assumptions for FP register layout.
