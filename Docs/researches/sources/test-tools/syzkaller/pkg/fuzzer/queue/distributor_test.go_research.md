# sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor_test.go

## Purpose
This test documents and validates the soft VM-avoidance policy in `Distributor`.

## Important APIs, Types, And Functions
`TestDistributor` uses a `Plain` queue wrapped by `Distribute`, submits a reusable `Request`, mutates its `Avoid` list, and calls `dist.Next(vm)` for VM IDs 0 and 1.

## Control Flow
The test first checks pass-through with no avoidance. It then sets `Avoid` to VM 0, verifies VM 0 receives nil while VM 1 receives the request, then submits again and loops until VM 0 eventually receives it after the violation threshold. Finally it sets both active VMs in `Avoid` and expects immediate dispatch.

## State And Persistence Behavior
The test exercises delayed queue state, active VM sequence tracking, and `Request.delayedSince`.

## Dependencies And Integration Points
It depends only on `queue` package types and `testify/assert`. It supports the triage rerun behavior used by fuzzer jobs.

## Risks
The eventual-release loop has no explicit iteration cap, relying on the implementation's fixed 1000-tick cutoff.

## Test Signals
Assertions cover pass-through, delay, undelay on alternate VM, violation after repeated polling, and no delay when every active VM is avoided.
