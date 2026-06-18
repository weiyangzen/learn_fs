# sources/sync-backup/syncthing/lib/model/mocks/folderSummaryService.go

Purpose: this generated counterfeiter fake implements `model.FolderSummaryService` for tests. It lets tests stub service behavior, set default or per-call returns, inspect call counts and arguments, and retrieve a consolidated invocation map.

Important API surface: the fake has `Serve` and `Summary` methods matching the real interface. For each method it exposes `Calls` to install a stub, `CallCount`, `ArgsForCall`, `Returns`, and `ReturnsOnCall`. It also exposes `Invocations` for all recorded calls. The compile-time assertion `var _ model.FolderSummaryService = new(FolderSummaryService)` guarantees interface compatibility.

Control flow: each fake method locks its method-specific mutex, records arguments, captures the current stub and configured return values, records the invocation in the shared map, unlocks, and then calls the stub if present. If no stub is set, a per-call return overrides the default return; otherwise the default return is used. This lock-then-unlock-before-stub pattern avoids holding fake internals locked while user test code executes.

State and persistence behavior: all state is in-memory test state: argument slices, return structs, per-call return maps, stubs, and invocation records. There is no persistence. The invocation map copy returned by `Invocations` copies the map but not the nested slices, which is standard for these generated fakes but means callers should treat it as observational test data rather than mutable isolated state.

Dependencies and integration points: it imports `context`, `sync`, and the real `model` package. Tests that need a `FolderSummaryService` can use this fake without starting a suture service. It is generated from the `go:generate` directive in `folder_summary.go`.

Risks: because it is generated, manual edits would be overwritten. Default zero returns can hide missing test setup unless tests assert call counts or configure explicit returns. The fake is concurrency-aware for its own bookkeeping, but returned pointers such as `*model.FolderSummary` are not deep-copied.

Test signals: there are no tests for the fake itself. Its correctness signal is successful compilation against `model.FolderSummaryService` and the behavior of tests that depend on call recording.
