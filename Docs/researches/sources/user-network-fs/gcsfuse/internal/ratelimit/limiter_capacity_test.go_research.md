## sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity_test.go

### Purpose
`limiter_capacity_test.go` validates rate/window input handling and capacity calculation.

### Important APIs, Types, And Functions
The testify suite `LimiterCapacityTest` exercises `ChooseLimiterCapacity`. Helpers validate less-than-or-equal-to-zero rate and window errors.

### Control Flow
Tests call the helper with invalid rates, invalid windows, an undersized rate/window combination that yields capacity zero, and a normal case where `20 Hz` over `10s` yields capacity `4`.

### State, Persistence, And Dependencies
No state is persisted. Dependencies are `testing`, `time`, `fmt`, and testify.

### Integration Points
The tests protect configuration validation before token bucket construction.

### Risks
The zero-capacity test uses `time.Duration(1)` nanosecond, so the expected error describes a tiny window. Boundary cases around `math.MaxUint64`, infinity, and NaN are missing.

### Test Signals
Signals are focused on deterministic mathematical behavior and user-facing error strings.
