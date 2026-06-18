# sources/test-tools/syzkaller/tools/syz-testbed/targets.go

## Purpose
This file defines `syz-testbed` target strategies for benchmarking `syz-manager` performance and `syz-repro` reproduction success.

## Important APIs, types, and functions
- `TestbedTarget` interface abstracts job creation, stat persistence, and supported HTML tables.
- `targetConstructors` builds either `SyzManagerTarget` or `SyzReproTarget` from config.
- `SyzManagerTarget.NewJob`, `SupportsHTMLView`, and `SaveStatView` implement round-robin manager benchmarking and CSV/bench output.
- `SyzReproTarget`, `SyzReproInput`, `QueryTitle`, `NewJob`, `SupportsHTMLView`, and `SaveStatView` implement crash-log selection and repro benchmarking.

## Control flow
Manager jobs choose checkouts round-robin and assign monotonically increasing instance IDs. Repro target construction collects input logs either by walking a directory or sampling crash logs from a workdir while honoring skip regexps and `CrashesPerBug`. Repro jobs choose checkouts round-robin, lazily parse input titles per checkout, skip unparsable logs, and choose the least-run available input for that checkout.

## State and persistence behavior
Targets keep in-memory counters, input run counts, skip flags, and duplicate-title map under mutexes. `SaveStatView` writes target-specific CSV files and averaged bench files under caller-provided stats directories.

## Dependencies and integration points
Uses local instance constructors, stats/table methods, `collectBugs`, `pkg/osutil`, and `pkg/tool`. Repro inputs depend on checkout-specific reporters because parsing may vary with target config.

## Risks and edge cases
Repro target uses `regexp.MustCompile` for skip patterns, so invalid regexps panic during construction. Random sampling seeds from `time.Now().Nanosecond()`, limiting randomness entropy. `SyzManagerTarget.NewJob` assumes `checkouts` is non-empty. Repro title deduplication is global and mutable across checkouts, so display names depend on discovery order.

## Test signals
No direct tests. Useful tests include round-robin assignment, repro input sampling/skipping, duplicate title naming, least-run selection, invalid input handling, and stat file generation.
