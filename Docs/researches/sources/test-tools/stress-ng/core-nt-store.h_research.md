# sources/test-tools/stress-ng/core-nt-store.h

Purpose: conditionally exposes non-temporal store intrinsics for 128-bit, 64-bit, 32-bit, and double writes.

Important APIs/types: inline `stress_nt_store128`, `stress_nt_store64`, `stress_nt_store32`, and `stress_nt_store_double`, plus `HAVE_NT_STORE*` macros. Implementations select Clang builtins, GCC x86 builtins, or Intel intrinsic forms.

Control flow: preprocessor branches choose the best available implementation by type and architecture; unsupported combinations emit no helper and no availability macro.

State/persistence: no state; helpers write caller-provided memory and may bypass cache hierarchy.

Dependencies/integration: `core-arch.h`, optional intrinsic headers, SSE/x86_64 feature macros, int128 support, and compiler builtin detection.

Risks: callers must guard by availability macros, provide alignment, and apply ordering/fence semantics outside these helpers. The double GCC path is ABI-sensitive.

Test signals: Clang/GCC/ICC and x86/non-x86 builds, guarded users, and cache/memory stressors that validate written values.
