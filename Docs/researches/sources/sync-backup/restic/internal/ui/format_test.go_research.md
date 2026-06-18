<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format_test.go -->
# sources/sync-backup/restic/internal/ui/format_test.go

## Purpose
Tests and benchmarks UI formatting helpers.

## Important APIs and Control Flow
Tests cover byte formatting thresholds, percentage formatting, byte parsing with suffixes and overflow/invalid cases, display width for ASCII/Unicode, quoting of control and invalid text, and truncation across ASCII and wide runes. Benchmarks measure truncate performance. Control flow is table-driven with shared equality assertions.

## State, Persistence, Dependencies, and Integration
State is local test cases only. Dependencies include Unicode fixtures and shared test helpers.

## Risks and Test Signals
The suite is strong for formatting edge cases, though terminal font ambiguity means exact real display width can still vary.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format_test.go -->
