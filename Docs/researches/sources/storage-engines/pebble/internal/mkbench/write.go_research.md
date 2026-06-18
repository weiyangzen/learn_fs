<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write.go -->
# sources/storage-engines/pebble/internal/mkbench/write.go

Purpose: implements the `mkbench write` command, parsing raw write-throughput benchmark logs into top-level and per-run JSON summaries.

Important APIs/types: `getWriteCommand`, `writePoint`, `rawWriteRun`, `writeRunSummary`, `writeRun`, `cookedWriteRun`, `writeWorkload`, `writeLoader`, `newWriteLoader`, `loadCooked`, `loadRaw`, `addRawRun`, `cookSummary`, `cookWriteSummary`, `cookWriteRunSummaries`, `outputWriteRunSummary`, and `parseWrite`.

Control flow and state: `parseWrite` loads existing `summary.json` to seed cooked workload/day pairs, walks raw data, skips already-cooked days, parses compressed or plain logs matching `BenchmarkRaw...`, groups points by workload/day/raw path, computes optimal ops/sec splits with `findOptimalSplit`, writes merged top-level summaries sorted by date, and writes per-run raw summaries. Errors reading individual raw files are printed and skipped; output file errors are returned.

Persistence and integration: reads raw `data` trees and previous `write-throughput/summary.json`; writes `summary.json` and provenance-preserving `*-summary.json` files. Integrates with Cobra, gzip/bzip2 readers, `split.go`, `prettyJSON`, and `walkDir`. Risks include division by zero if a writeRun has no raw runs, scanner token limits on very long lines, skipping all files for a cooked workload/day even if new logs appear, stderr-only parse errors, and path-layout assumptions. Tests cover from-scratch and incremental fixture generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write.go -->
