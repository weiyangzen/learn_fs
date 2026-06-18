# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/rules.c

`rules.c` parses, expands, stores, prints, and incrementally updates plumber rules. It supports input stacks with includes, variable assignment, variable expansion with quoting and `$` substitutions, regex compilation for `matches`, validation of object/verb combinations, port declarations, pattern/action grouping, and readback formatting.

Rulesets consist of pattern rules over message fields plus plumb actions such as `to`, `start`, or `client`. Empty lines terminate rulesets. Include depth is capped, port names reject reserved entries, and `/sys/lib/plumb` is searched for relative includes.

`writerules()` supports partial writes to `/mnt/plumb/rules`, parsing complete rules as blank-line-delimited chunks arrive and finishing on close/truncation.
