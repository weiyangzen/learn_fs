<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/aarch64/asmdefs.h -->
# sources/storage-engines/foundationdb/flow/aarch64/asmdefs.h
- Purpose: Shared AArch64 assembly macros for function entries, ELF GNU property notes, BTI/PAC hints, CFI metadata, and ILP32 argument sanitization.
- Important APIs/types/functions: `BTI_C`, `BTI_J`, `PACIASP`, `AUTIASP`, `GNU_PROPERTY`, `ENTRY_ALIGN`, `ENTRY`, `ENTRY_ALIAS`, `END`, `L`, `PTR_ARG`, and `SIZE_ARG`.
- Control flow: Assembly files include this header to emit standardized prolog labels and metadata. On `__aarch64__`, it emits BTI/PAC support notes by default; otherwise it provides simpler entry macros.
- State and persistence behavior: No runtime state. It affects object-file metadata and symbol layout.
- Dependencies and integration points: Used by `memcmp.S` and `memcpy.S`. Depends on assembler support for AArch64 hints, ELF note sections, and CFI directives.
- Risks: GNU property emission must match toolchain/linker expectations. The comment contains a spelling typo in Branch Target Identification but behavior is macro-defined. ILP32 sanitization is required for ABI correctness.
- Test signals: Assembler/build success on supported AArch64 configurations, object property inspection, and runtime execution of the assembly routines are the validation points.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/aarch64/asmdefs.h -->
