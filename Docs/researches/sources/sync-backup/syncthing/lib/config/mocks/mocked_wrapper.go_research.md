# sources/sync-backup/syncthing/lib/config/mocks/mocked_wrapper.go

## sources/sync-backup/syncthing/lib/config/mocks/mocked_wrapper.go

Purpose: Generated counterfeiter fake for the `config.Wrapper` interface, used by tests in packages that need configurable wrapper behavior.

Important APIs/types/functions: Type `mocks.Wrapper` implements every method from `config.Wrapper`: config accessors, mutation methods, folder/device lookup/list methods, ignored state, lifecycle `Serve`, subscription methods, and `suture.Service`. For each method it provides a stub field, mutex-protected call recording, fixed return values, per-call returns, call-count accessors, args-for-call helpers where applicable, and `Invocations`.

Control flow and state: Each fake method locks its method mutex, records arguments, captures the current stub/return configuration, records the invocation under a shared invocation mutex, unlocks, then either calls the stub, returns a per-call value, or returns the default configured value. The final compile-time assertion ensures it satisfies `config.Wrapper`.

Dependencies and integration: Imports `context`, `sync`, `config`, and `protocol`. Regenerated from the `go:generate` directive in `wrapper.go`.

Risks and test signals: Because it is generated, manual edits are risky and will be overwritten. The fake’s locking supports concurrent tests, but returned slices/maps are whatever the test configures and are not deep-copied by the mock itself.
