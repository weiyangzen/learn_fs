# sources/storage-engines/pebble/internal/binfmt/hexdump_test.go

Purpose: Datadriven tests for hex dump formatting.

APIs and types: Exercises `HexDump` with `read-file` and `sequential` commands, configurable width, offsets, and data slices.

Control flow and state: Each datadriven command builds or reads bytes, slices by position/length, then returns formatted dump output for comparison.

Persistence and dependencies: Reads testdata files only. Depends on `datadriven`, `os.ReadFile`, and testify require.

Integration points: Protects diagnostic output used by binary format explainers.

Risks: Does not test invalid widths. Output changes require datadriven fixture updates.

Test signals: Good text-format regression coverage for row/offset/ascii rendering.
