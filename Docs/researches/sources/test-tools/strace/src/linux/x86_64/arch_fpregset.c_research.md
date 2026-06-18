<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_fpregset.c

Purpose: decodes x86_64 `NT_FPREGSET` floating-point register-set payloads for ptrace/regset printing.
Important APIs/types/functions: `arch_decode_fpregset`, `struct_fpregset`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY_UPTO`, and mpers fallback to i386 for `MPERS_IS_m32`.
Control flow: rejects zero or non-8-byte-aligned sizes, fetches up to the known structure size, prints fields only when present by `offsetof`, and emits `more_data_follows` for larger kernel payloads.
State and persistence behavior: stateless; only reads tracee memory. Dependencies and integration points: paired with `arch_fpregset.h` and generic regset decoding.
Risks: size/offset mistakes can hide partial regsets or over-read changed kernel layouts. Test signals: ptrace regset tests with full, partial, and oversized fpregset buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.c -->
