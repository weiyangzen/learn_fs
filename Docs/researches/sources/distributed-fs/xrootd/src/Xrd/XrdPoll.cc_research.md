## sources/distributed-fs/xrootd/src/Xrd/XrdPoll.cc

Purpose: implements common poller infrastructure and selects the platform poll backend. It starts poller threads, balances link attachment, detaches links, formats poll stats, and defines termination protocol behavior.

Important APIs/types/functions: `XrdPoll` constructor creates a command pipe. `Attach()` chooses the poller with the fewest attached fds and calls backend `Include()`. `Detach()` calls backend `Exclude()` and decrements counters. `Finish()` swaps in a local `XrdPoll_End` protocol and records error text. `getRequest()` reads backend commands from the pipe. `Setup()` creates `XRD_NUMPOLLERS` pollers and starts threads. `Stats()` emits XML counters.

Control flow: configuration calls `Setup(numfd)`. `XrdLink::Activate()` calls `Attach()`. Backends receive fd events and schedule link jobs. `Disable()`/`Enable()` are backend-specific. On fatal events `Finish()` marks a link for termination before scheduling close behavior.

State/persistence: static `Pollers[3]`, `doingAttach`, per-poller pipe fds, attached/enabled/event/interrupt counters, and pipe read buffer state. No durable persistence.

Dependencies/integration: uses `XrdPollE` on Linux and `XrdPollPoll` elsewhere, plus `XrdLink`, `XrdProtocol`, `XrdScheduler`, `XrdSysFD`, and logging/tracing.

Risks: `Setup()` reuses one stack `XrdPollArg` per poller thread and relies on semaphore synchronization before the next iteration mutates it. `Poll2Text()` returns heap strings, so callers must handle ownership if needed. `Attach()` assumes all `Pollers` are initialized.

Test signals: run with Linux epoll and non-Linux poll backends, attach balancing across three pollers, detach underflow detection, termination idempotence, partial command pipe reads, and stats formatting.
