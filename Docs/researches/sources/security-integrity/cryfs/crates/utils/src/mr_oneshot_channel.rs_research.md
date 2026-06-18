# sources/security-integrity/cryfs/crates/utils/src/mr_oneshot_channel.rs

Purpose: multi-receiver one-shot channel: a single sender publishes one cloneable value to any number of receivers.

Important APIs/types/functions: `channel<T>() -> (Sender<T>, Receiver<T>)`; `Sender::send(self, value)`; `Sender::subscribe`; `Receiver::recv` and `try_recv`; `RecvError`. Inner state is `Empty`, `Filled(T)`, or `Closed`.

Control flow: sender consumes itself to send, stores value under mutex, then notifies waiters. Dropping an unsent sender marks `Closed`. Receivers create a notification future before checking state to avoid races, clone the filled value, or return `RecvError` if closed.

State/persistence: in-memory mutex-protected state and Notify. Filled values remain stored as long as channel inner exists.

Dependencies/integration: useful for broadcasting one async initialization result.

Risks: `T: Clone` is required for receiving. Sending after non-empty state panics, though consumption normally prevents reuse. Mutex poisoning panics via unwrap.

Test signals: tokio tests cover basic send/recv, multiple receivers, waiting before send, sender drop, try_recv, concurrent receivers, non-cloneable sender intent, and recv after sent.
