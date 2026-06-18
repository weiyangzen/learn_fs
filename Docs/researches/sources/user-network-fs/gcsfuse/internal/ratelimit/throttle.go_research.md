## sources/user-network-fs/gcsfuse/internal/ratelimit/throttle.go

### Purpose
`throttle.go` defines a concurrency-safe throttling abstraction backed by `golang.org/x/time/rate.Limiter`.

### Important APIs, Types, And Functions
`Throttle` exposes `Capacity()` and `Wait(ctx, tokens)`. `NewThrottle(rateHz, capacity)` returns a `limiter` wrapper. `limiter.Capacity` returns burst size, and `limiter.Wait` delegates to `WaitN`.

### Control Flow
Callers construct a token bucket with a per-second rate and burst capacity. Each `Wait` request blocks until the requested number of tokens is available or the context is canceled. The interface requires callers to request no more than `Capacity`.

### State, Persistence, And Dependencies
State is inside `rate.Limiter`; it is safe for concurrent access. There is no persistence. Dependencies are `x/time/rate` and context.

### Integration Points
`throttled_reader.go` uses it for byte bandwidth, and `throttled_bucket.go` uses it for operation rate limiting.

### Risks
The implementation casts `uint64` tokens and capacity to `int`; extremely large capacities can overflow on 32-bit platforms or unrealistic configurations. The precondition `tokens <= capacity` is not enforced by the wrapper.

### Test Signals
`throttle_test.go` runs integration-style concurrent arrival simulations and checks throughput is close to min(arrival rate, limit rate).
