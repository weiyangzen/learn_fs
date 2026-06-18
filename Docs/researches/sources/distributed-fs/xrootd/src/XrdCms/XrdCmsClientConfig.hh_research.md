# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.hh

## Purpose
Declares the configuration holder and parser API for CMS client roles.

## Important APIs, Types, and Functions
Defines `configHow`, `configWhat`, `Configure()`, timing fields (`ConWait`, `RepWait`, `RepDelay`, etc.), path/identity fields (`CMSPath`, `myHost`, `myName`, `myVNID`, `cidTag`), manager lists, performance monitor pointer/interval, and selection modes `FailOver`/`RoundRob`.

## Control Flow
Consumers construct this object, call `Configure()`, then use the populated public fields to initialize manager connections, local sockets, performance reporting, and request handling.

## State and Persistence Behavior
Most state is public mutable configuration. Private fields store parser/plugin intermediates and role booleans. The destructor frees owned linked lists and heap strings.

## Dependencies and Integration Points
Includes `XrdOucTList` and conversion utilities. Forward-declares stream/error/perf classes. Used by CMS finder/client manager setup.

## Risks and Edge Cases
Public mutable fields make invariants dependent on call order and caller discipline. Ownership is manual C allocation/free. Defaults encode operational policy and should be reviewed when changing protocol timing.

## Test Signals
Constructor default tests, destructor leak checks, and configuration parser integration tests are the main signals.
