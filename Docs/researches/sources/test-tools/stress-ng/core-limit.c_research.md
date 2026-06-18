# sources/test-tools/stress-ng/core-limit.c

## Purpose

This module pushes process resource limits toward their maximums, or applies user-specified overrides for selected memory-related limits. It helps stress-ng exercise systems without being constrained by conservative inherited shell limits.

## Important APIs, Types, And Functions

`stress_rlimit_t` maps `RLIMIT_*` resources to optional stress-ng setting names. `stress_limit_set` applies an override from settings when available, rounding down to page size, otherwise sets soft limit equal to hard limit. The public API is `stress_limit_max_set`.

## Control Flow

`stress_limit_max_set` iterates the compile-time `limits` array and calls `stress_limit_set` for each resource. Afterward, it applies an explicit `"max-fd"` setting to `RLIMIT_NOFILE` when configured. All `setrlimit` failures are ignored by design.

## State And Persistence Behavior

The module mutates process resource limits. These changes persist for the process and inherited children. It has no internal mutable state.

## Dependencies And Integration Points

It depends on `stress_setting_get`, page-size lookup, shim resource type definitions, and command-line settings such as `limit-as`, `limit-data`, `limit-stack`, and `max-fd`.

## Risks And Test Signals

Risks include over-tightening limits through user overrides, failures under privilege/container restrictions, and page-size rounding to zero for very small values. Test signals include successful soft-to-hard promotion, override rounding, ignored failures, and `max-fd` application.
