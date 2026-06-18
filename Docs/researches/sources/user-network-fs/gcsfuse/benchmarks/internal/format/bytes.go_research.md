## sources/user-network-fs/gcsfuse/benchmarks/internal/format/bytes.go

Purpose: Formats byte counts into human-readable binary units for benchmark output.

Important APIs/types/functions: `Bytes(v float64) string` chooses GiB, MiB, KiB, or bytes and returns a two-decimal `fmt.Sprintf` string.

Control flow: threshold switch from largest to smallest unit using powers of two.

State and persistence: stateless pure formatting.

Dependencies and integration points: used by benchmark programs to print throughput and total bytes.

Risks: negative values print as bytes; all output has two decimals; units are binary but input semantics are caller-defined.

Test signals: no direct tests in this subset; benchmark output indirectly exercises it.
