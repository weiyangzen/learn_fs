<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter.go -->
# sources/sync-backup/restic/internal/backend/limiter/limiter.go

## Purpose
Declares the bandwidth limiter interface shared by backend wrappers and HTTP transports.

## Important APIs, Types, And Functions
Limiter exposes Upstream, UpstreamWriter, Downstream, DownstreamWriter, and Transport.

## Control Flow
No implementation flow in this file; it defines how upload/download readers, writers, and RoundTrippers are wrapped.

## State And Persistence Behavior
No state. Implementations hold any token buckets or policy data.

## Dependencies And Integration Points
Depends on io and net/http. Used by limiter backends, static limiter, rclone stdio wrapping, and backend factories.

## Risks And Edge Cases
Implementations must preserve reader/writer semantics and close behavior; incorrect direction choice throttles the wrong traffic.

## Test Signals
Validated by static limiter and backend limiter tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter.go -->
