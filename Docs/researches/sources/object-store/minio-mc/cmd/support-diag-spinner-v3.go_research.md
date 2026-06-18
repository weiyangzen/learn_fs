<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag-spinner-v3.go -->
# sources/object-store/minio-mc/cmd/support-diag-spinner-v3.go

Purpose: provides progress spinner handling for the current `madmin.HealthInfo` diagnostics stream used by support diagnostics.

Important APIs/types/functions: `receiveHealthInfo` is the only exported-to-package function. It decodes a JSON stream of `madmin.HealthInfo`, tracks expected health sections, and updates `mpb` spinner bars as each section arrives.

Control flow: the function creates an `mpb.Progress` with a wait group, defines a small `progressSpinner` struct, registers section predicates for CPU, disk, net, OS, memory, process, server config, system errors/services/config, and admin info, then decodes the response in a goroutine. Each decoded health frame updates the accumulated `info`; when a predicate is satisfied or the final admin server list is observed, the corresponding spinner is marked complete. `pg.Wait()` blocks until all spinners finish.

State and persistence: all state is in memory: accumulated health info, wait group, progress bars, and decode error. No disk or server state is changed.

Dependencies and integration points: used by `fetchServerDiagInfo` for `madmin.HealthInfoVersion`. It depends on `colorjson.Decoder`, `madmin.HealthInfo`, `mpb`, and shared console color helpers from the diagnostics file.

Risks and test signals: if a stream ends before any condition satisfies and no final server info is sent, the wait group can block. Tests should simulate complete, EOF, and partial streams, especially ensuring EOF clears the error and all expected bars complete for final frames.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag-spinner-v3.go -->
