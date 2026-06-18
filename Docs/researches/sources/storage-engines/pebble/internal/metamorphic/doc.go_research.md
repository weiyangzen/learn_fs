<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/doc.go -->
# sources/storage-engines/pebble/internal/metamorphic/doc.go

Purpose: package documentation for `internal/metamorphic`, identifying it as the entry point for Pebble's internal metamorphic tests.

Important APIs/types/functions: no executable APIs are defined here. The file declares package `metamorphic` and points readers to the public-ish `pebble/metamorphic` package where the core generator, runner, compare logic, and options live.

Control flow and state: none. This file affects documentation and package identity only.

Dependencies and integration: the package contains `meta_test.go` and reduction helpers in this subset, plus many external dependencies in `github.com/cockroachdb/pebble/metamorphic`. Risks are documentation drift if entry points or package layering change. Test signal is indirect: if the package name or comments became inconsistent, Go tooling would still compile, so only human review catches most doc drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/doc.go -->
