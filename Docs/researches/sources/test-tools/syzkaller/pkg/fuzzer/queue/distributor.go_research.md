# sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor.go

## Purpose
`Distributor` wraps a request source and distributes requests across VMs while honoring soft `Avoid` preferences used during triage reruns. It delays requests that should avoid the requesting VM when other active VMs are available.

## Important APIs, Types, And Functions
`Distributor` stores an underlying `Source`, sequence counter, delayed queue, active-VM array, and stats for delayed, undelayed, and violated requests. `Distribute` constructs it and registers stats. `Next(vm int)` records activity, first tries delayed work suitable for the VM, then pulls from the source until it finds a request that can run immediately or no request exists. `delay`, `delayed`, `noteActive`, `hasOtherActive`, and `contains` implement the policy.

## Control Flow
On each VM request, `Next` calls `noteActive`. If a delayed request is runnable on this VM, it returns it. Otherwise it pulls fresh requests; if a request wants to avoid this VM and some other recent active VM is available, the request is queued as delayed and polling continues. Delayed requests are eventually released after about 1000 sequence ticks even if this violates avoidance.

## State And Persistence Behavior
All state is in memory. `active` is an atomic pointer to a slice of atomic VM sequence markers and can grow when higher VM IDs appear. Delayed requests store `delayedSince` on the request itself. Stats accumulate process-wide observations.

## Dependencies And Integration Points
It depends on the queue `Source`/`Request` model and `stat`. `triageJob.deflake` uses `Avoid` to prefer not rerunning a program on the same executor that first observed it.

## Risks
Avoidance is intentionally soft; if active VM detection is stale or no alternative remains, a request can run on an avoided VM. The active slice growth path assumes `active` is non-nil by the time `hasOtherActive` is called; `Next` establishes that through `noteActive`. The 1000-tick threshold is heuristic.

## Test Signals
`distributor_test.go` verifies normal pass-through, avoid-delay behavior, eventual violation when only the avoided VM polls, and immediate dispatch when all active VMs are in the avoid set.
