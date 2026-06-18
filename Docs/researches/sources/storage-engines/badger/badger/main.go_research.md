# sources/storage-engines/badger/badger/main.go

Purpose: entrypoint for the Badger CLI binary.

Important flow: starts an HTTP debug server loop trying ports 8080 through 9079 on `0.0.0.0`, registers zPages trace handling at `/z`, sets block profile rate and `GOMAXPROCS(128)`, checks jemalloc allocation through `z.CallocNoRef`, prints allocator stats, runs `cmd.Execute`, then prints remaining allocated bytes and leak details.

State and persistence: no database state directly; it opens a debug network listener and writes diagnostics to stdout. Dependencies include net/http/pprof, OpenTelemetry zpages, Ristretto allocator utilities, Cobra command package, and go-humanize. Risks: binding pprof on all interfaces exposes debug endpoints when the CLI is run in shared environments, the goroutine loops forever on busy ports, and hard-coded `GOMAXPROCS(128)` overrides runtime defaults. Test signals should include CLI startup in port-conflict environments, pprof exposure review, and leak-report behavior at process end.
