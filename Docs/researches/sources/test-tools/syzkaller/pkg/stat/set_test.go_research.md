# sources/test-tools/syzkaller/pkg/stat/set_test.go

## Purpose

This test suite validates metric creation, collection formatting, graph history, compression, distributions, rates, and concurrent access.

## Important APIs, Types, And Flow

`TestSet` covers counters, external metrics, custom formatters, distribution means, graph/no-graph options, panic paths, and UI sorting by level/name. `TestSetRateFormat` checks second/minute/hour formatting thresholds. `TestSetHistoryCounter`, `TestSetHistoryRate`, and `TestSetHistoryDistribution` manually tick a small history registry to verify compression semantics. `TestSetStress` starts concurrent goroutines that create metrics, add values, read values, collect UI, render graphs, and tick for one second.

## State, Dependencies, Risks, And Test Signals

The tests use `newSet(4, false)` to avoid the global ticker and make history deterministic. They intentionally call negative `Add` in counter history tests, which relies on conversion behavior when read back as `int`. Stress testing is probabilistic and mainly race-detector oriented. Missing coverage includes Prometheus registration errors and duplicate-name behavior beyond unknown-option panic.
