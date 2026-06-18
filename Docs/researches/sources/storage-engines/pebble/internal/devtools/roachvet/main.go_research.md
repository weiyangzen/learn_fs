# sources/storage-engines/pebble/internal/devtools/roachvet/main.go

## Purpose
`main.go` assembles Pebble’s custom vet binary. It wires Cockroach/Pebble-specific analyzers and configures `errcheck` exclusions before handing control to Go’s `unitchecker`.

## Important APIs, Types, And Functions
`errcheckExcludes` lists functions and methods whose returned errors are intentionally ignored. `initErrCheck` writes that list to a temporary file, configures `errcheck.Analyzer.Flags` with the `exclude` path, and returns a cleanup closure. `main` defers cleanup and calls `unitchecker.Main` with `deferloop`, `errcheck`, `nocopy`, `returnerrcheck`, and `ForbiddenImportsAnalyzer`.

## Control Flow
Startup creates a temp exclude file and panics on any setup error. `unitchecker.Main` then runs analyzers under the vet/unitchecker protocol. Deferred cleanup removes the temporary file on process exit.

## State And Persistence Behavior
The only persisted state is a temporary excludes file in the system temp directory, removed by cleanup. The analyzer set is static at binary build time.

## Dependencies And Integration Points
It depends on Cockroach lint analyzers, `kisielk/errcheck`, and `golang.org/x/tools/go/analysis/unitchecker`. This file is part of the `internal/devtools/roachvet` command and is typically invoked by build or CI scripts.

## Risks And Edge Cases
Because `errcheck` is configured through a temp file, failure to create/write/close the file panics and prevents vet from running. `errcheck.Analyzer.Flags.Set` errors are ignored; unexpected flag changes upstream would not be reported. The exclusion list must be maintained as APIs and acceptable ignored errors change.

## Test Signals
CI vet runs are the primary signal. A useful smoke test builds the command and confirms all analyzers register and errcheck accepts the generated exclusion file.
