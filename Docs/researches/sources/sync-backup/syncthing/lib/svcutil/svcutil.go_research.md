# sources/sync-backup/syncthing/lib/svcutil/svcutil.go

Purpose: utilities for Suture-managed services, fatal/no-restart error tagging, exit status values, event logging specs, and context-wrapped calls.

Important APIs and control flow: `FatalErr` wraps an error with an `ExitStatus` and reports `Is(suture.ErrTerminateSupervisorTree)`. `NoRestartErr` wraps errors so `errors.Is(..., suture.ErrDoNotRestart)` succeeds. `AsService` wraps a function as `ServiceWithError`, storing the most recent error behind a mutex and converting context-like errors to plain errors unless the service context is actually canceled. `OnSupervisorDone` adds a service that runs a callback after supervisor context completion. `SpecWithDebugLogger` and `SpecWithInfoLogger` configure Suture specs. `infoEventHook` suppresses repeated identical termination logs. `CallWithContext` runs a blocking function in a goroutine and returns context error if canceled first.

State and persistence: in-memory service error state and closure-local previous termination event.

Dependencies and integration: central to `syncthing.App`, STUN calls, failure reporting, and other supervised services.

Risks: `CallWithContext` leaks the goroutine until the function returns. Error identity conversion is deliberate but can hide timeout semantics from Suture. No tests in this subset.
