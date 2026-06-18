# sources/test-tools/strace/bundled/linux/include/uapi/linux/elf-em.h

Purpose: defines Linux-visible ELF `e_machine` constants for architectures and legacy/interim machine IDs.

Important APIs/types/functions: constants include common IDs such as `EM_386`, `EM_MIPS`, `EM_S390`, `EM_ARM`, `EM_X86_64`, `EM_AARCH64`, `EM_RISCV`, `EM_BPF`, `EM_LOONGARCH`, plus legacy/interim values like `EM_ALPHA`, `EM_CYGNUS_M32R`, `EM_S390_OLD`, and `EM_CYGNUS_MN10300`.

Control flow: no control flow; these are numeric identifiers used in ELF headers.

State and persistence behavior: values are persisted in ELF binaries, kernel modules, core files, and object files. The header also documents historical IDs that Linux rejects or keeps for compatibility.

Dependencies: no includes beyond the guard.

Integration points: strace and related tooling can decode ELF machine fields when inspecting exec/module-related data. Kernel ELF loaders and user tools use the same numeric IDs.

Risks: some IDs alias or document history: `EM_MIPS_RS3_LE` and `EM_MIPS_RS4_BE` both use 10, and some old/interim IDs remain nonstandard. Decoders should print exact names where possible without assuming one-to-one architecture mapping for obsolete values.

Test signals: tests should cover modern architectures, `EM_BPF`, `EM_LOONGARCH`, duplicate MIPS legacy value handling, and fallback rendering for unknown `e_machine` numbers.
