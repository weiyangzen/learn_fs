# sources/test-tools/stress-ng/core-interrupts.h

## Purpose

This header declares interrupt accounting and reporting helpers used around stressor execution.

## Important APIs, Types, And Functions

It exposes start/stop counter collection, failure checking, YAML/report dumping, and TLB/IPI summary collection. It relies on `stress_interrupts_t` and `stress_list_item_t` from project-wide definitions.

## Control Flow

Callers collect counters at run boundaries, check failure status after stopping, and optionally dump aggregate reports.

## State And Persistence Behavior

Counter storage is caller-owned. The implementation reads kernel counters but does not mutate them.

## Dependencies And Integration Points

The header integrates with stressor stats and YAML reporting. It is used by run orchestration to detect system-level interrupt failures.

## Risks And Test Signals

The header contract depends on `STRESS_INTERRUPTS_MAX` matching the implementation metadata. Compile-time assertions and per-instance stat allocation tests are useful.
