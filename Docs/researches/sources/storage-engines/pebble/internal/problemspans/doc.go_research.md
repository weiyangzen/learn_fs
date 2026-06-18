<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/doc.go -->
# sources/storage-engines/pebble/internal/problemspans/doc.go

Purpose: package documentation for tracking key spans that are problematic for a bounded time and checking/excising active spans.

Important content: describes span registration with expiration, overlap detection, span excision, and level-based organization with concurrent operations.

Control flow and state: none; package declaration only.

Dependencies and integration: documents the behavior implemented by `Set` and `ByLevel`. Risks are doc drift, especially because concurrency safety differs between `Set` (not safe) and `ByLevel` (safe), and because expiration behavior depends on monotonic time. Test signal is indirect through package tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/doc.go -->
