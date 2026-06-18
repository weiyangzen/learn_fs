# sources/security-integrity/cryfs/crates/utils/src/panic.rs

Purpose: defines `safe_panic!`, a panic macro that avoids aborting from double panic during unwinding.

Important APIs/types/functions: exported `safe_panic!` checks `std::thread::panicking()`. If already panicking, it prints to stderr; otherwise it calls `panic!`.

Control flow: macro expands inline at call sites. It is used by `AsyncDropGuard::drop` where panicking during cleanup diagnostics could otherwise double-panic.

State/persistence: no persistent state; may write to stderr.

Dependencies/integration: exported at crate root by `#[macro_export]`, despite module being private in `lib.rs`.

Risks: during unwinding it logs instead of panicking, so tests may need stderr inspection to catch secondary errors. In normal flow it still panics.

Test signals: unit tests cover normal panic, formatting, and no abort during a caught panic with a destructor call.
