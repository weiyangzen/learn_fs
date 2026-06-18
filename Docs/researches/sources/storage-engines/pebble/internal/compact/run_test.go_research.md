# sources/storage-engines/pebble/internal/compact/run_test.go

## Purpose
This file tests hard output table split limits derived from grandparent overlap and L0 flush split keys.

## Important APIs, Types, And Functions
`TestTableSplitLimit` uses datadriven commands to build a manifest `Version`, initialize an `L0Organizer`, and call `Runner.TableSplitLimit` for requested start keys.

## Control Flow
The `define` command parses version debug text and prints the version plus flush split keys when present. The `split-limit` command constructs a minimal `Runner` with `Grandparents`, `L0SplitKeys`, and `MaxGrandparentOverlapBytes`, then prints either no limit or the selected key for each input.

## State And Persistence Behavior
All state is in-memory manifest/test metadata. No compaction outputs are written.

## Dependencies And Integration Points
It depends on `datadriven`, `manifest.ParseVersionDebug`, `manifest.NewL0Organizer`, `testutils.CheckErr`, and `Runner.TableSplitLimit`.

## Risks And Edge Cases
The test focuses only on split-limit selection, not actual writer boundary validation or range span carryover. It is sensitive to manifest ordering and L0 organizer flush split behavior.

## Test Signals
Expected datadriven output verifies limits from max grandparent overlap and from flush split keys, including the minimum of both when both apply.
