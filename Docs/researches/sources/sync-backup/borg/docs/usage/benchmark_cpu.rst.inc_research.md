# sources/sync-backup/borg/docs/usage/benchmark_cpu.rst.inc

Purpose: generated reference for `borg benchmark cpu`, a CPU-bound throughput benchmark for Borg internals.

Important APIs and control flow: command shape is `borg [common options] benchmark cpu [options]`; the only command-specific option is `--json`. It creates input data in memory, runs miscellaneous Borg operations, and reports throughput.

State and persistence: no repository data is required or persisted; benchmark data is in-memory.

Dependencies and integration points: integrates with common logging/output options and JSON output consumers. Meaningful results depend on machine load and memory availability.

Risks: benchmark variance is high if the host is busy or paging. The docs must stay aligned with actual measured operations in the benchmark implementation.

Test signals: parser help generation, successful text and JSON benchmark output, and JSON schema stability for automation using `--json`.
