# sources/security-integrity/cryfs/crates/utils/tests/at_exit_signals.rs

Purpose: Integration-tests `AtExitHandler` behavior for process-wide termination signals (`SIGTERM`, `SIGINT`, and `SIGQUIT`). The test binary isolates signal raising from the rest of the suite.

Important APIs and types: It uses `cryfs_utils::at_exit::AtExitHandler`, `signal_hook` signal constants, `libc::raise`, channels, barriers, and a module-level `LOCK`. `signal_test` serializes each signal scenario and sleeps afterward.

Control flow: Each test acquires the global mutex, installs one or more handlers, raises a signal with `libc::raise`, waits for channel/barrier evidence, then sleeps 1.5 seconds to avoid the double-signal detector threshold in `cryfs_utils::at_exit`. Tests cover individual signals, multiple separated signals, complex callback payloads, multiple handlers, dropping a handler before a later signal, and handler thread naming.

State and persistence behavior: State is process-wide signal handler registration and per-test channel/barrier state. No files are persisted. Because `AtExitHandler` is global/process-affecting, tests are deliberately serialized even within this isolated integration binary.

Dependencies and integration points: This file validates the signal path used by shutdown/cleanup handling in the utilities crate. It complements process-exit tests and any cleanup mechanisms that rely on `AtExitHandler`.

Risks: Signal tests are inherently timing-sensitive and process-global. If another test or library registers competing signal iterators for the same signals in this binary, delivery semantics could change. The explicit sleep makes the suite slower but avoids a hard process exit from the double-signal guard.

Test signals: Evidence is channel receipt within 10 seconds, two receipts for two separated signals, barrier completion for three handlers, absence of callback after drop, and thread name equal to `atexit:my-custom-handler`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/tests/at_exit_signals.rs` completely for this pass (203 lines, 5947 bytes).
