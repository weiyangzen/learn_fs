# sources/test-tools/syzkaller/pkg/subsystem/match_test.go

## Purpose

This file tests `PathMatcher` behavior for overlapping include rules, exclusions, documentation paths, and the intended include-before-exclude semantics.

## Important APIs, Types, And Functions

`TestPathMatcher` creates synthetic `Subsystem` values with path rules for ARM, documentation, and overlapping IRQ/devicetree files. `TestPathMatchOrder` verifies that a rule with include `^a/b/.*$` and exclude `^a/.*$` does not match `a/b/c`.

## Control Flow, State, Dependencies, And Integration

The tests build `MakePathMatcher` directly, call `Match`, and assert with `assert.ElementsMatch` or `assert.Empty`. There is no filesystem or persistence. They isolate `PathMatcher` from the higher-level extractor and Linux subsystem list, making failures easier to attribute to matching logic.

## Risks And Test Signals

The tests catch duplicate returns when multiple include rules match one subsystem and ensure a path can match multiple subsystems. They also enforce that exclusion is scoped per rule, not a global pre-filter. Because the production matcher returns map-key order, the tests correctly ignore result order.
