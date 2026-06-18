# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.hh

## Purpose
`XrdSsiServReal.hh` declares the concrete service implementation used on the client side of SSI routing. It specializes `XrdSsiService` with endpoint session pooling and resource reuse support.

## Important APIs and Types
The class overrides `ProcessRequest` and `Stop`, and adds `Recycle` and `StopReuse` for session lifecycle management. Private `Alloc`, `GenURL`, and `ResReuse` are the implementation hooks used by the `.cc` file. State includes a resource cache map from string keys to `XrdSsiSessReal*`, two mutexes, a manager node string, a free-session list, active/free counts, and stop state.

## Control Flow
The declaration shows a split between request processing, free-list recycling, and cache eviction. `Recycle` is called by sessions after unprovision/shutdown; `StopReuse` lets a session or service remove a reusable key before it becomes invalid.

## State and Persistence
All state is volatile. The constructor duplicates the manager contact string and sets the maximum retained session objects from `hObj`. The destructor frees `manNode` and free sessions.

## Dependencies and Integration Points
It depends on `XrdSsiService`, `XrdSsiSessReal`, `XrdSsiResource`, STL `map`, and `XrdSysMutex`. It is instantiated by SSI provider/client plumbing outside this work item.

## Risks and Test Signals
Raw session pointers in the cache and free list make ownership discipline central. Tests should check destructor cleanup with free sessions, cache erasure on reuse stop, active count accounting, and that `Stop(true)` refuses active sessions while `Stop(false)` allows completion-driven deletion.
