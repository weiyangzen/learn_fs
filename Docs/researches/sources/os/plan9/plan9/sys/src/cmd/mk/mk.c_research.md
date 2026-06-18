# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/mk.c

Core build algorithm for `mk`.

Key functions:
- `mk(target)` builds dependency graph, clears made flags, repeatedly schedules work, waits for children, and reports up-to-date status.
- `clrmade()` resets graph nodes to `NOTMADE`.
- `work(node, parent, parc)` recursively determines readiness/out-of-date status and invokes recipes.
- `update(fake, node)` updates node status/time after recipe completion or failure.
- `outofdate(node, arc, eval)` compares times or invokes custom `P` program comparator.
- `pcmp()` runs custom comparison program via `pipecmd()`.

Behavior notes:
- Supports “pretending” missing intermediate files are made when safe.
- Equal timestamps are treated as out-of-date to avoid races.
- `-k` allows continuing after errors by marking failed work as being made/fake.
- Archive missing members are considered out-of-date.
