# File Research: sources/os/plan9/9front/sys/src/cmd/kc/k.out.h

Object-format and architecture enum header for SPARC `k` tools. It defines symbol-name and register counts, special general and floating registers, all assembler/compiler opcodes (`A*`), address name/type constants (`D_*`), ranlib `SYMDEF`, and the `Ieee` split-double representation used when serializing floating constants.

The register comments document compiler allocation policy: integer temporaries grow upward from `R7`, external integer registers grow downward from `R6`, and floating register variables occupy even F registers. These constants are shared by assembler, compiler, linker, and related diagnostics, making enum stability important for object compatibility.
