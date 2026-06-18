# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiClient.cc

## Purpose
Implements the global SSI client provider (`XrdSsiProviderClient`) used by applications to obtain `XrdSsiService` instances for contact endpoints. It lazily initializes logging, scheduling, XrdCl environment defaults, and contact dispatch policy.

## Important APIs, Types, And Functions
- Namespace globals include `clMutex`, `schedP`, `clEnvP`, `contactN`, `maxTCB`, `maxCLW`, `maxPEL`, `initDone`, timeout-set flags, `hiResTime`, and request-dispatch mode `rDisp`.
- `XrdSsiClientProvider : XrdSsiProvider` implements `GetService()`, `SetCBThreads()`, `SetConfig()`, `SetSpread()`, and `SetTimeout()`.
- Private helpers `SetLogger()` and `SetScheduler()` create `XrdSysLogger`, configure trace/log callbacks, allocate `XrdScheduler`, and start it.
- Global `XrdSsiProvider *XrdSsiProviderClient` points to a static provider instance.

## Control Flow
`GetService()` performs first-use initialization under `clMutex`: create logger, scheduler, XrdCl default environment, install effectively infinite defaults for data server TTL, request timeout, and stream timeout unless explicitly set, configure poller count, and optionally disable IP shuffling for none/round-robin dispatch. It then validates the contact string. Multi-contact or non-singleton contacts are registered in `XrdNetRegistry` under generated `contact-N` names with optional rotation. Singleton contacts are validated and formatted through `XrdNetAddr`. On success, it returns a new `XrdSsiServReal` with the resolved contact and hold value.

Configuration calls update globals under the same mutex where needed. `SetCBThreads()` caps callback threads and derives network worker count from callback count when not supplied. `SetConfig()` accepts `cbThreads`, `hiResTime`, `netThreads`, `pollers`, and `reqDispatch`. `SetTimeout()` writes XrdCl environment keys for connection retry/window, idle close, request timeout, and stream timeout, marking user-set timeouts to prevent first-use defaults from overriding them.

## State And Persistence
The provider is process-global. It persists scheduler, logger, XrdCl environment settings, contact registry entries, dispatch policy, and thread-count configuration for the process lifetime. It does not persist service state across process restarts.

## Dependencies And Integration Points
Depends on XRootD scheduler/trace, XrdCl default environment, XrdNet address/registry utilities, SSI logger/provider/service classes, scale utilities, and atomic/mutex wrappers. It is the client-side entry point for SSI services and returns `XrdSsiServReal` objects.

## Risks And Edge Cases
- `initDone = true` uses direct assignment rather than `Atomic_SET`; with C++11 `std::atomic<bool>` this is valid, but legacy macro modes may differ.
- `SetScheduler()` checks `clEnvP` before setting worker threads, but first-use initialization calls `SetScheduler()` before assigning `clEnvP`, causing it to fetch the default environment inside the helper.
- Contact registry names use an atomic post-increment counter; overflow is unlikely but not handled.
- Empty contact fails early, but malformed multi-contact errors depend on `XrdNetRegistry::Register()`.
- Global settings after first service creation may not retroactively affect already-created scheduler/environment behavior.

## Test Signals
Tests should cover first-use lazy initialization, empty contact failure, singleton contact validation, multi-contact registry creation with round-robin/random/no dispatch, callback/network thread settings, timeout settings before and after initialization, high-resolution logging via option and environment, and concurrent `GetService()` calls.
