# sources/security-integrity/cryfs/crates/utils/src/progress.rs

Purpose: Provides an abstraction over interactive progress indicators so application code can create spinners/progress bars without binding directly to console output. It offers console implementations backed by `indicatif` and silent no-op implementations for tests or non-interactive modes.

Important APIs and types: `ProgressBarManager` creates `Spinner` and `Progress` instances. `ConsoleProgressBarManager` creates `ConsoleSpinner` and `ConsoleProgress`; `SilentProgressBarManager` creates `SilentSpinner` and `SilentProgress`. `Spinner::finish` consumes the spinner, while `Progress` supports `inc`, `inc_length`, and consuming `finish`.

Control flow: Console constructors create an `indicatif::ProgressBar`, set messages and styles, enable steady ticking for spinners, and wrap a `ConsoleProgressImpl` in an outer `Arc`. Increment methods forward to the inner indicatif progress bar. Finishing attempts `Arc::into_inner`, enforcing that no clones remain, then drops the implementation. `ConsoleProgressImpl::drop` calls `finish_with_message`.

State and persistence behavior: Runtime state is the shared progress bar and static message. There is no persistence. The extra `Arc` is load-bearing because `indicatif::ProgressBar` is itself cloneable; the wrapper wants finish/drop side effects only when the final user clone is consumed.

Dependencies and integration points: Depends on `indicatif`, `Arc`, and `Duration`. The manager traits let higher-level CryFS code be generic over console and silent progress behavior.

Risks: `finish` panics if clones still exist, so users must coordinate clone lifetimes. Console styling unwraps template construction, which is acceptable for fixed templates but would panic if changed to invalid templates. Silent implementations intentionally discard all progress information, so tests using them only validate call safety, not display correctness.

Test signals: Unit tests focus on silent spinner/progress behavior, clone/copy behavior, manager factory output, and no-op increments/finish. Console behavior is not directly asserted beyond compile-time integration.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/progress.rs` completely for this pass (271 lines, 8132 bytes).
