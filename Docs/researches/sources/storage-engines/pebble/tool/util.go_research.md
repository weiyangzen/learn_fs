# Research: sources/storage-engines/pebble/tool/util.go

## Purpose
`tool/util.go` contains shared parsing, formatting, traversal, and file-processing helpers for Pebble CLI tools. It normalizes user-provided key syntax and output formatting across SSTable, WAL, DB, and related commands.

## Important APIs, Types, And Functions
`key` implements Cobra flag parsing for raw strings, `hex:` bytes, `raw:` bytes, and `crdb:` formatted Cockroach keys. `keyFormatter` and `valueFormatter` implement formatter flags with built-ins `null`, `quoted`, `pretty`, `size`, `pretty:<comparer>`, and one-percent `fmt` patterns. Comparer-aware `setForComparer` methods install `FormatKey` and `FormatValue` hooks when available.

Formatting helpers include `formatKey`, `formatSeqNumRange`, `formatKeyRange`, `formatKeyValue`, and `formatSpan`. `walk` recursively traverses an FS in sorted order. `processFiles` walks CLI arguments, filters extensions, opens files, creates a 128 MiB cache and handle, constructs readers, invokes a callback, and closes resources.

## Control Flow
Formatter `Set` methods parse the user spec and set a formatter function. Value formatting wraps the selected formatter to render values prefixed with `blob-value:` in a special debug-friendly form. `processFiles` routes each candidate file through open, cache creation, reader construction, processing, and deferred cleanup. Directory traversal is depth-first and deterministic because entries are sorted.

## State And Persistence
The helpers do not write persistent state. Transient state includes formatter selection, optional comparer override names, buffers used by callers, cache handles, opened files, and constructed readers. `timeNow` is a package variable for test substitution.

## Dependencies And Integration Points
The file integrates Cobra flag interfaces, Cockroach key parsing, Pebble cache management, internal key formatting, keyspan formatting, sstable comparer registries, and `vfs.FS`. Most tool subcommands depend on these helpers for consistent output.

## Risks And Edge Cases
Formatter validation only accepts specs with exactly one `%` for custom `fmt` output; invalid specs fail flag parsing. Pretty formatting mutates formatter functions depending on table comparer unless the user explicitly chose a formatter. `processFiles` creates a new cache per file, which is simple but can be heavy over many files. Recursive traversal reports errors to stderr and keeps going, so partial failures are possible.

## Test Signals
Signals include parsing of `hex:`, `raw:`, and `crdb:` keys; formatter selection and comparer overrides; suppression via `null`; size output; blob-value display; sorted recursive traversal; extension filtering; reader close behavior; and stable key/value formatting in golden CLI tests.
