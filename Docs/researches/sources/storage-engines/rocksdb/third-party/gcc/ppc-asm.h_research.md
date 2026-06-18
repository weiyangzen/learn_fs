# sources/storage-engines/rocksdb/third-party/gcc/ppc-asm.h

Purpose: vendored GCC runtime header providing PowerPC assembler register aliases and function-definition macros for multiple PowerPC ABIs. RocksDB carries it under third-party code for architecture-specific assembly compatibility.

Important APIs/macros: defines numeric aliases for general registers `r0`-`r31`, condition registers `cr0`-`cr7`, floating registers `f0`-`f31`, optional VSX `f32`-`f63` and `vs0`-`vs63`, and optional AltiVec `v0`-`v31`. `XGLUE`/`GLUE` concatenate tokens. ABI-specific macros include `FUNC_NAME`, `JUMP_TARGET`, `FUNC_START`, `HIDDEN_FUNC`, and `FUNC_END` for ELFv2, 64-bit descriptor ABIs, AIX descriptors, and generic ELF/PIC cases. Under `IN_GCC`, CFI macros map to gas directives when available. On 32-bit Linux it emits a `.note.GNU-stack` section.

State and persistence: no runtime state. It controls assembler symbol layout and unwind metadata at compile time.

Dependencies/integration: used by assembly sources that need portable PowerPC function prologues across GNU toolchains. It may include `auto-host.h` when compiled inside GCC.

Risks and test signals: macro definitions are ABI-sensitive; changing them can break symbol names, TOC setup, hidden visibility, or executable-stack markings. Vendored license terms are GPL with GCC Runtime Library Exception. Test signals are architecture build/link tests on ppc32, ppc64 ELFv1, ppc64 ELFv2, PIC, PC-relative, VSX, and AltiVec configurations.
