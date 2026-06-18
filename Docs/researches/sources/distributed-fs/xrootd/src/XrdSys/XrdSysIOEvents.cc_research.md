## sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.cc

Purpose: implements the common channel/poller state machine for XrdSys non-blocking I/O event dispatch, leaving backend poll-set mechanics to platform `.icc` files.

Important APIs/types/functions: local sentinel pollers `pollInit`, `pollWait`, and `pollErr1`; `BootStrap::Start()` starts the poll thread; `Channel` methods implement `Delete`, `Enable`, `Disable`, `SetFD`, `SetCallBack`, `Reset`; `Poller` methods implement `Create`, `Attach`, `Detach`, callback execution, command-pipe I/O, timeout queue management, `Stop`, and `WakeUp`.

Control flow: `Poller::Create()` creates a CLOEXEC pipe, constructs the backend via `newPoller()`, starts a bound thread, and waits on a semaphore for readiness. A `Channel` starts attached to `pollInit`; first `Enable()` transitions through `pollWait`, includes the fd in the backend poll set, then modifies event masks. Poller callbacks call `CbkXeq()`, which removes/updates timeouts, handles fatal errors, drops the channel lock before invoking user callbacks, then either detaches or re-arms deadlines. `Stop()` sends a pipe command, closes pipes, disables channels, invokes optional stop callbacks, and runs backend shutdown.

State and persistence: per-channel state includes fd, callbacks, event masks, read/write timeouts, deadlines, status, poll-set membership, deferred modifications, and faults. Per-poller state includes attached and timeout linked lists, command pipe fds, wake-pending atomic flag, poll thread id, locks, and static parent PID/max time. No durable persistence.

Dependencies and integration: uses `XrdSysFD`, `XrdSysPthread`, `XrdSysAtomics`, `XrdSysE2T`, platform headers, and includes epoll/kqueue/poll/port backends by preprocessor.

Risks: high concurrency surface: callback deletion, fd lifetime, lock handoff, deferred modify, and timeout rearming must remain consistent. Header warns callers must disable/delete channels before closing fds. Wakeup ordering relies on atomics plus `toMutex`.

Test signals: enable/disable/read/write/error events, callback deleting channel, external deletion during callback, `SetFD(-1)` before close, timeout auto-rearm and `optTOM`, poller stop callback, backend command pipe partial reads, and stress with many concurrent channel mutations.
