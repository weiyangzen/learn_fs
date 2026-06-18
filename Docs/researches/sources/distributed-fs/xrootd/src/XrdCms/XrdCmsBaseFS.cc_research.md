# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.cc

## Purpose
Implements the CMS base filesystem existence checker and throttled lookup queue. It decides whether file existence can be answered locally, must be queued/rate-limited, or should be forwarded to other cluster nodes.

## Important APIs, Types, and Functions
Implements `Bypass()`, `Exists(XrdCmsRRData&, XrdCmsPInfo&, int)`, `Exists(char*, int, int)`, `hasDir()`, `Init()`, `Limit()`, `Pacer()`, `Queue()`, `Runner()`, `Start()`, and `Xeq()`. Thread entry points call `Pacer()` and `Runner()`.

## Control Flow
`Exists()` first checks whether local stat is enabled; otherwise it queues/forwards. With local stat, optional directory-miss caching can reject paths early. Rate limiting can allow inline execution, enqueue into a paced queue, or force queueing. `Pacer()` moves pending requests to the runnable queue at the configured rate; `Runner()` executes them and calls the configured callback. `Xeq()` performs final stat/forward callback logic.

## State and Persistence Behavior
In-memory state includes directory presence/miss hash entries with lifetimes, request queues with semaphores and high-water accounting, rate-limit counters, and mode flags. Filesystem state is only observed through `Config.ossFS->Stat`; prepare queue state can make missing staged files appear pending.

## Dependencies and Integration Points
Depends on CMS config, prepare queue, trace, `XrdOss` stat interface, SFS flags, timers, semaphores, and protocol request data. Callback `cBack` integrates lookup completion with higher-level routing/selection.

## Risks and Edge Cases
`Bypass()` logs to `std::cerr`, which may be noisy in production. Queue overrun handling logs but still enqueues. Path buffers are temporarily modified in-place around directory stat checks, requiring mutable/null-terminated input and careful restoration. Bad stat errors are rate-limited by counters and may hide intermittent problems.

## Test Signals
Tests should cover local stat online/pending/directory/missing cases, prepare-queue pending fallback, directory miss/present cache, rate-limit queue flow, queue overrun logging, callback behavior for local and non-local modes, and mutable path restoration.
