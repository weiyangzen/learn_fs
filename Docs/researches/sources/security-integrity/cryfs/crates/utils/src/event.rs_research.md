# sources/security-integrity/cryfs/crates/utils/src/event.rs

Purpose: cloneable one-shot async event primitive.

Important APIs/types/functions: `Event` wraps `Arc<EventImpl>` containing `AtomicBool triggered` and `tokio::sync::Notify`. APIs are `new`, `Default`, `trigger`, and `wait`.

Control flow: `trigger` atomically flips the flag and notifies all waiters once. `wait` creates a `notified()` future before checking the flag to avoid missed notifications, then awaits only if not triggered.

State/persistence: one in-memory boolean latch; cannot reset.

Dependencies/integration: used by rustfs test mock initialization and other task synchronization points.

Risks: one-shot semantics only. Notify does not store per-event counts; correctness relies on the pre-check notified future pattern.

Test signals: tokio tests cover trigger-before-wait, wait-before-trigger, multiple waiters, idempotent trigger, clone sharing, and default state.
