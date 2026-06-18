# Research: sources/storage-engines/rocksdb/utilities/trace/replayer_impl.h

- **Purpose:** Declares RocksDB's concrete trace replayer implementation and worker argument bundle for background replay.
- **Important APIs/types/functions:** `ReplayerImpl` overrides `Prepare`, `Next`, `Execute`, `Replay`, and `GetHeaderTimestamp`. Private helpers are `ReadHeader`, `ReadTrace`, and static `BackgroundWork`. `ReplayerWorkerArg` carries a `Trace`, file version, execution handler pointer, error callback, and result callback.
- **Control flow:** Exposes the public replayer lifecycle while keeping trace decoding and background execution internals private.
- **State and persistence behavior:** Tracks reader ownership, mutex-protected reading, atomic preparation/end flags, header timestamp, execution handler, environment pointer, and parsed trace format version. Replay persistence is performed through the execution handler against the DB supplied in the constructor.
- **Dependencies:** Includes DB/env/status/trace interfaces, trace record/result APIs, `rocksdb/utilities/replayer.h`, and trace replay helper declarations.
- **Integration points:** Concrete implementation behind public replay construction; interoperates with any `TraceReader`, including `FileTraceReader`.
- **Risks:** `exec_handler_` is shared with worker args as a raw pointer, so `Replay` must not outlive the `ReplayerImpl` object and callbacks must not retain it. Atomic booleans protect state visibility but do not make the whole replayer API safely reentrant.
- **Test signals:** Header contract should be validated through public replayer API tests for prepare/next/execute/replay lifecycle and multi-thread background execution.
