# sources/storage-engines/tikv/components/pd_client/src/tso.rs

Purpose: Implements the low-level Timestamp Oracle worker used by `PdClient::get_tso`. It batches many caller timestamp requests into streaming PD `TsoRequest`s and distributes returned physical/logical timestamps back to individual oneshot callers.

Important APIs/types/functions: `TimestampOracle` owns a bounded `mpsc::Sender<TimestampRequest>` plus a close watch receiver. `TimestampOracle::new` opens the PD bidirectional TSO stream and spawns the `TSO_WORKER_THREAD`. `get_timestamp(count)` returns a future resolving to a composed `txn_types::TimeStamp`. `closed()` lets callers observe worker termination. `run_tso` drives sending and receiving futures concurrently. `TsoRequestStream` implements `Stream<Item=(TsoRequest, WriteFlags)>` and batches up to `MAX_BATCH_SIZE`. `allocate_timestamps` maps one PD tail timestamp and response count back to queued requests.

Control flow: Callers send a `TimestampRequest` containing a oneshot sender and requested count. The worker drains the bounded channel into a request group, sends one `TsoRequest` with the summed count, tracks the group in a FIFO pending queue, and waits for matching PD responses. The response handler pops the oldest group and calculates each caller's logical timestamp by subtracting offsets from PD's tail logical value.

State and persistence behavior: State is in-memory: bounded request channel, pending request queue, and close notification. It persists nothing locally. `MAX_PENDING_COUNT` and the `AtomicWaker` prevent unbounded pending growth by pausing request-stream polling until responses drain.

Dependencies and integration points: It uses `grpcio`, `kvproto::pdpb::PdClient`, `futures`, `tokio` channels, TiKV thread naming utilities, and `PD_PENDING_TSO_REQUEST_GAUGE`. It is created by `pd_client::util::PdConnector`/`Client` when a PD connection is established or reconnected.

Risks: The worker assumes PD responses arrive in request order and with exactly matching `count`; mismatch errors terminate the worker. Logical subtraction assumes PD returned a sufficient tail logical value. `request_tx` is bounded to `MAX_BATCH_SIZE`, so overloaded callers apply backpressure. The spawned thread uses `expect`, so thread creation failure panics.

Test signals: No local tests. Important integration signals are TSO monotonicity, count batching, worker shutdown after stream error, pending gauge accuracy, and reconnection replacing the oracle.
