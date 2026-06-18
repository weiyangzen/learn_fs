# File Research: sources/windows/winfsp/src/dll/service.c

Implements WinFsp service hosting, including SCM mode, console fallback mode, stop/control dispatch, service-context validation, and logging.

Main lifecycle:
- `FspServiceRunEx()` creates a service object, enables console mode, runs the loop, returns the service exit code, and deletes the object.
- `FspServiceCreate()` allocates `FSP_SERVICE`, stores callbacks, initializes status/stop critical sections, and sets accepted controls.
- `FspServiceLoop()` serializes dispatcher use with `FspServiceLoopLock`, installs a temporary service table, and calls `StartServiceCtrlDispatcherW`.
- If SCM connection fails with `ERROR_FAILED_SERVICE_CONTROLLER_CONNECT` and console mode is allowed, it creates a console event, installs `FspServiceConsoleCtrlHandler`, starts a thread that invokes `FspServiceMain`, then waits for console stop signal.

Status and stop handling:
- `FspServiceSetStatus()` updates selected `SERVICE_STATUS` fields under lock and reports to SCM or signals the console event on stop.
- `FspServiceRequestTime()` increments checkpoint and wait hint.
- `FspServiceStop()` guards against concurrent stop, transitions to `STOP_PENDING`, calls `OnStop`, then either reports stopped or reverts status on failure.
- `FspServiceStopLoop()` can stop the currently registered service from a helper thread.

Control handling:
- `FspServiceCtrlHandler()` handles stop/shutdown, pause/continue unsupported, interrogate success, and delegates unknown controls to `OnControl`.
- `FspServiceConsoleCtrlHandler()` maps Ctrl-C/break/close/shutdown to the console stop event; close/shutdown may sleep to allow cleanup; logoff is ignored.

Context and logging:
- `FspServiceIsInteractive()` detects visible process window station.
- `FspServiceContextCheck()` verifies a token is session 0 and either LocalSystem or a member of Service SID; can duplicate current process token if none is supplied.
- `FspServiceLogV()` writes UTF-8 text to stderr when interactive, otherwise logs through `FspEventLogV`.

Concurrency details:
- Uses SRW locks for global service loop/table protection.
- Uses critical sections for per-service status and stop serialization.
- Finalization intentionally only closes the console event on explicit unload.
