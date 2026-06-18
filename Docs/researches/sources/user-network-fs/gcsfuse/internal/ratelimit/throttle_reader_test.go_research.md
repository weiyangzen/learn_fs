## sources/user-network-fs/gcsfuse/internal/ratelimit/throttle_reader_test.go

### Purpose
`throttle_reader_test.go` verifies that `ThrottledReader` gates reads through a throttle, respects throttle capacity, and preserves reader error/short-read semantics.

### Important APIs, Types, And Functions
It defines `funcReader`, `funcThrottle`, and `ThrottledReaderTest`. Tests cover throttle invocation, throttle errors, wrapped reader invocation, wrapped errors/EOF, full reads, short reads followed by second reads, and read-size clipping to throttle capacity.

### Control Flow
Setup creates a no-op throttle and wraps a function-backed reader. Each test replaces throttle or reader callbacks, calls `Read`, and checks token counts, buffer slices, total bytes, and propagated errors.

### State, Persistence, And Dependencies
State is local function callbacks and context. Dependencies are `io`, `context`, and testify suite/assertions.

### Integration Points
The suite protects byte-rate limiting used by throttled GCS readers, especially when consumers ask for reads larger than the limiter burst.

### Risks
The tests do not cover context cancellation with the real `rate.Limiter`, zero-length reads, or readers that return `(0, nil)`, which could spin in the production loop.

### Test Signals
Signals are strong for capacity clipping, pre-read throttling, short-read refill behavior, and preserving EOF/non-EOF errors.
