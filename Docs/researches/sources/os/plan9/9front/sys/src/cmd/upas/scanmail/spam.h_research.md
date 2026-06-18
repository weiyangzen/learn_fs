# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/spam.h

This header defines the scanmail spam-pattern model shared by `scanmail`, `testscan`, and the pattern parser/matcher implementation. Actions are ordered by severity: `Dump`, `HoldHeader`, `Hold`, `SaveLine`, `Lineoff`, with `Lineoff` required last for control-flow assumptions in `scanmail.c`.

The core structures distinguish literal-string matchers (`Spat` hash buckets) from compiled regex matchers (`Reprog`) under `Pattern`, grouped by action in `Patterns`. Constants set scan limits, hash size, pattern type tags, and HTML/header/body read bounds.

The header also publishes the global pattern table, debug/header/cmd globals, and helper APIs for message reading, canonical conversion, base64 conversion, pattern parsing, matching, and match printing. It is a narrow contract for the spam scanner subsystem.
