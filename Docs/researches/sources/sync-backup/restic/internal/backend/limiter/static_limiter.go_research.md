<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter.go -->
# sources/sync-backup/restic/internal/backend/limiter/static_limiter.go

## Purpose
Implements a fixed upload/download byte-rate limiter using x/time/rate token buckets.

## Important APIs, Types, And Functions
Limits, NewStaticLimiter, staticLimiter Upstream/Downstream methods, Transport, rateLimitedReader/Writer, consumeTokens, and toByteRate are the important APIs.

## Control Flow
NewStaticLimiter creates upload/download buckets when limits are positive. Reader and writer wrappers wait for tokens after each read/write. Transport wraps request bodies and response bodies in the correct directions.

## State And Persistence Behavior
State is in rate.Limiter buckets shared by all wrappers from the staticLimiter instance; there is no repository persistence.

## Dependencies And Integration Points
Depends on context, io, net/http, and x/time/rate. Used by backend and HTTP transport wrapping.

## Risks And Edge Cases
Shared buckets mean concurrent operations share total bandwidth. consumeTokens loops for chunks larger than bucket burst, so context-less waits use context.Background and cannot be canceled directly.

## Test Signals
static_limiter_test.go covers wrapping identity, read/write throttling, response body close propagation, nil body, and nil limiter cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter.go -->
