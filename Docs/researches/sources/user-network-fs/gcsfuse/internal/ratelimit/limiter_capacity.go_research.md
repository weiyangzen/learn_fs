## sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity.go

### Purpose
`limiter_capacity.go` computes a token bucket burst capacity that bounds transient overrun within a chosen time window.

### Important APIs, Types, And Functions
The exported function is `ChooseLimiterCapacity(rateHz float64, window time.Duration) (uint64, error)`. It uses a constant `N = 50`, corresponding to about 2 percent overrun.

### Control Flow
The function rejects non-positive or infinite rates and non-positive windows. It converts the window to seconds, computes `floor(windowSeconds * rateHz / N)`, and errors if the result is less than one or cannot fit in `uint64`. Otherwise it returns the capacity.

### State, Persistence, And Dependencies
There is no state or persistence. Dependencies are `fmt`, `math`, and `time`.

### Integration Points
Throttle setup can use this helper to choose a burst size for `NewThrottle` so operation or byte rates remain close to configured limits over operational windows.

### Risks
Very low rates or very small windows cannot be represented with a useful token bucket capacity and return errors. NaN rates are not explicitly rejected; comparisons with NaN make the final capacity check fail with the token-bucket error rather than the illegal-rate error.

### Test Signals
Tests cover negative/zero rates, negative/zero windows, zero computed capacity, and a normal expected capacity. Infinite and NaN rates are not covered.
