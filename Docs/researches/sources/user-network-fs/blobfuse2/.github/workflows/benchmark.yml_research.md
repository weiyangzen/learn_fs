# sources/user-network-fs/blobfuse2/.github/workflows/benchmark.yml

## Purpose
This workflow runs weekly and manually triggered benchmark jobs across x86 and ARM64 self-hosted runners, storage account types, and cache modes.

## Important APIs, Types, and Functions
The workflow defines a `PerfTesting` job with a matrix over runner config, `TestType`, and `CacheMode`. It calls the local composite action `.github/actions/perftesting` and passes GitHub token plus Azure storage account secrets.

## Control Flow
On Sunday schedule or `workflow_dispatch`, the job runs with `max-parallel: 1` to reduce performance interference. Each matrix row checks out the selected ref and delegates all setup, build, mount, FIO execution, and benchmark publication to the composite action.

## State and Persistence Behavior
The workflow itself persists benchmark pages/data through the composite action on `main`. Runner state includes installed packages, local mount/cache paths, and possible ARM RAID setup.

## Dependencies and Integration Points
It depends on self-hosted labels `1ES.Pool=blobfuse2-benchmark` and `1ES.Pool=blobfuse2-benchmark-arm`, Azure storage secrets, and the benchmark action's `benchmarks` branch convention.

## Risks and Edge Cases
The action relies on `matrix.TestType` and `matrix.CacheMode`, so renaming those matrix keys breaks the composite action. `TestType` only lists standard and premium even though the composite action has HNS inputs. Long timeout and self-hosted state make stale mounts or disk layout drift likely.

## Test Signals
Signals include all matrix rows completing, FIO result JSON files existing, benchmark branch updates, and no cross-run contamination in `/mnt/blob_mnt` or `/mnt/localssd/tempcache`.
