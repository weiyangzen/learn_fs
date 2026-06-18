# sources/storage-engines/pebble/internal/ewma/ewma_bytes.go

## Purpose
`ewma_bytes.go` implements a per-byte exponential moving average estimator for values sampled over variably sized byte blocks, such as compression ratios over recently processed data.

## Important APIs, Types, And Functions
`Bytes` stores `alpha`, weighted `sum`, `totalWeight`, and deferred unsampled `gap`. `Init(halfLife)` configures alpha so samples one half-life of bytes old have half weight. `Estimate` returns `sum / totalWeight` and is NaN before sampling. `NoSample(numBytes)` advances the logical byte position without changing the value. `SampledBlock(numBytes, value)` decays prior weights by the gap plus block size and adds the new block’s weight. `decay(n)` returns `(1-alpha)^n`.

## Control Flow
Unsampled bytes accumulate in `gap` to avoid repeated decay work. When a sampled block arrives, the estimator applies one decay for `gap + numBytes`, resets the gap, computes the new block weight as `1 - decay(numBytes)`, and adds weighted value/weight.

## State And Persistence Behavior
State is in-memory and cumulative over calls. Reinitialization clears all prior samples. Negative `NoSample` or nonpositive `SampledBlock` panics only when invariants are enabled; otherwise the call is ignored.

## Dependencies And Integration Points
It depends on `math`, `cockroachdb/errors`, and `invariants`. It is a low-level internal estimator intended for byte-stream metrics elsewhere in Pebble.

## Risks And Edge Cases
`Init` should be called with a positive half-life; zero or negative values produce invalid alpha behavior. `Estimate` before any sample returns NaN by design. Numerical stability is addressed with `Expm1` and `Log1p`, important for large half-lives.

## Test Signals
`ewma_bytes_test.go` validates estimate behavior after samples/gaps and verifies half-life decay over a wide range of byte distances.
