## sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_reader.go

### Purpose
`throttled_reader.go` creates an `io.Reader` that limits read bandwidth by acquiring tokens before reading from an underlying reader.

### Important APIs, Types, And Functions
`ThrottledReader(ctx, r, throttle)` returns a `*throttledReader`. `throttledReader.Read` enforces capacity, waits for tokens, and loops until the requested slice is filled or the wrapped reader returns an error.

### Control Flow
For each read call, the buffer is clipped to `throttle.Capacity()` if larger. The reader waits for exactly the clipped length. It then repeatedly calls the wrapped reader, advancing the slice by bytes read, until all acquired bytes are served or an error such as EOF occurs.

### State, Persistence, And Dependencies
State is the context, wrapped reader, and throttle references. There is no persistence. Dependencies are `io` and context.

### Integration Points
`throttled_bucket.go` uses this for GCS reader egress limiting. It can also wrap any stream where bytes correspond to throttle tokens.

### Risks
If a wrapped reader returns `(0, nil)`, the loop can spin because `len(p)` does not decrease and `err` remains nil. The implementation charges for requested bytes, not bytes actually returned; short reads with EOF can consume more tokens than delivered. Zero-capacity throttles would clip every read to zero and wait for zero tokens.

### Test Signals
`throttle_reader_test.go` covers throttle invocation, capacity clipping, full reads, short reads, EOF, and error propagation. It does not cover `(0, nil)` or real-time rate behavior.
