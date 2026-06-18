# sources/test-tools/syzkaller/executor/nocover.h

Purpose: No-op coverage adapter for targets without executor coverage support.

Important APIs: defines empty `cover_open`, `cover_enable`, `cover_reset`, `cover_collect`, `cover_protect`, `cover_mmap`, and `cover_unprotect` functions with the same signatures expected by `executor.cc`.

State and dependencies: no state, no external dependencies beyond the common `cover_t` type.

Integration points: included by Fuchsia and Windows executor adapters.

Risks and tests: callers must not expect coverage buffers, signal collection, or comparisons when this header is active. Compile-time integration is the main test signal; runtime manager negotiation should avoid requesting unsupported coverage where appropriate.
