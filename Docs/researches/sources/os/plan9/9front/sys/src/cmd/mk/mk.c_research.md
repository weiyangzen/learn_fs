# File Research: sources/os/plan9/9front/sys/src/cmd/mk/mk.c

Drives target building and freshness decisions.

Key behavior:
- `mk()` builds a graph, clears made flags, repeatedly calls `work()`, waits for jobs, and reports up-to-date targets.
- `work()` recursively builds prerequisites, determines readiness/out-of-date status, supports pretend-made behavior, and schedules recipes with `dorecipe()`.
- `update()` records target completion and recomputes timestamps, including virtual targets and programmatic out-of-date checks.
- `outofdate()` compares timestamps or runs rule `P` programs, caching command results in `S_OUTOFDATE`.

Important dependencies: `graph`, `dorecipe`, `waitup`, `timeof`, `pipecmd`, `symlook`.

Notable risks:
- Equal timestamps are treated as out-of-date by design to avoid races.
- Pretend/unpretend logic is subtle and depends on parent freshness.
