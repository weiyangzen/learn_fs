## sources/user-network-fs/gcsfuse/benchmarks/internal/format/hertz.go

Purpose: Formats rates in Hz/KHz/MHz/GHz for benchmark output.

Important APIs/types/functions: `Hertz(v float64) string` selects decimal thresholds 1e3, 1e6, 1e9 and returns a two-decimal string.

Control flow: switch from GHz down to Hz.

State and persistence: stateless pure formatting.

Dependencies and integration points: used by stat/read/write benchmark reports.

Risks: uses `KHz` capitalization rather than SI `kHz`; negative values are formatted as Hz.

Test signals: no direct tests in this subset.
