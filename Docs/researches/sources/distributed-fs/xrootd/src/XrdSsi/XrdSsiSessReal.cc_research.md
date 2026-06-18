# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.cc

## Purpose
`XrdSsiSessReal.cc` implements the endpoint session object used by `XrdSsiServReal`. A session owns one `XrdCl::File` connection to an endpoint resource, queues one or more SSI task objects against it, handles asynchronous open/close events, and coordinates reusable-session shutdown.

## Important APIs and Functions
Public lifecycle methods implemented here include destructor cleanup, `InitSession`, `Provision`, `Run`, `TaskFinished`, `UnHold`, `Unprovision`, and `XeqEvent`. Private helpers `NewTask`, `RelTask`, and `Shutdown` allocate tasks, recycle/free them, and return the session to the service.

## Control Flow
`Provision` opens the endpoint file with optional refresh for retries and registers the session as the `XrdCl::ResponseHandler`. It immediately allocates a task and marks `inOpen`. `XeqEvent` handles the open completion: on failure it schedules errors on all pending tasks; on success it captures the endpoint `DataServer` property and sends queued requests. `Run` is used for an already held session and reserves the original channel entry before creating and sending a task. `TaskFinished` removes the task, releases the scale entry, and closes the endpoint when no non-held work remains.

## State and Persistence
Session state is in memory: session/task identifiers, endpoint file, task lists, free task list, resource key, resource/session names, endpoint node, open/held/reuse flags, user entry, and allocation budget. There is no disk persistence.

## Dependencies and Integration Points
The session integrates `XrdCl::File`, SSI request/task/agent utilities, global scheduler cleanup jobs, global `sidScale`, `XrdSsiServReal::Recycle`, and `XrdSsiTaskReal::SendRequest`. It uses a recursive session mutex plus a shared task mutex assigned to requests through `XrdSsiRRAgent::SetMutex`.

## Risks and Test Signals
Risks include object invalidation after `Shutdown`, callback ordering between task finish and open completion, leaked channel reservations when task creation fails, and held-session reuse after endpoint errors. Tests should cover open success/failure, multiple queued tasks before open completes, close failure recycling=false, unhold cleanup scheduling, retry refresh flag, `DataServer` property absence, and task ID wraparound boundaries.
