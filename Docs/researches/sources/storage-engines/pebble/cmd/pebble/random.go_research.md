<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/random.go -->
# sources/storage-engines/pebble/cmd/pebble/random.go

## Purpose
Implements the `--rate` flag parser and rate-limiter factory for benchmark commands.

## Important APIs, Types, and Functions
`rateFlag` embeds `randvar.Flag` and adds a fluctuation period plus original spec string. `newRateFlag`, `String`, `Type`, `Set`, and `newRateLimiter` implement Cobra/pflag value behavior and create a `rate.Limiter`.

## Control Flow
An empty spec is converted to a zero random variable and disables limiter creation. Non-empty specs are split on optional `/periodSeconds`; the left side is parsed by `randvar.Flag`, and the optional right side controls a goroutine that periodically changes limiter rate from the random distribution.

## State and Persistence Behavior
State is process memory: parsed random-variable configuration, duration, and spec string. No persistent state is written. A fluctuating limiter starts a ticker goroutine that runs for process lifetime; there is no explicit stop path.

## Dependencies and Integration Points
Depends on Pebble internal `randvar` and `rate` packages, `time`, string parsing, and CockroachDB errors. `main.go` binds it to shared benchmark flags, and individual benchmark runners assign `commonCfg.RateLimiter`.

## Risks and Edge Cases
`time.Duration(fluctuateDurationFloat) * time.Second` truncates fractional seconds before multiplying, so `0.5` becomes zero. The ticker goroutine is not stopped. Invalid split counts, random-variable specs, or period parsing return errors. A spec that evaluates to zero creates a limiter with zero rate.

## Test Signals
No direct tests. Useful checks include empty spec returning nil limiter, valid uniform/zipf specs, invalid parse errors, and fluctuating rate changes over time.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/random.go -->
