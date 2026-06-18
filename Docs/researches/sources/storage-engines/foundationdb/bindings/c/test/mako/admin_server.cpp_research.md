# sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.cpp

## Purpose
Implements Mako's forked admin server process for tasks that need isolated process-global FDB/TLS configuration.

## Important APIs, types, and functions
`AdminServer::start` forks, reconfigures the child logger, applies global options, sets up FDB network, starts a network thread, and handles serialized requests. `AdminServer::~AdminServer` sends `StopRequest` and waits. `getOrCreateDatabase` caches database handles by cluster file, though current dispatch only handles ping/stop.

## Control flow
The parent returns after fork. The child loops reading request variants, responds with `DefaultResponse`, stops on `StopRequest`, and uses an exit guard to stop/join the network thread.

## State and persistence behavior
Maintains process id, pipes, optional setup error, database cache, and network thread. No current request persists data.

## Dependencies and integration points
Uses Boost process pipes/serialization/variant, POSIX `fork`/`waitpid`, `fdb_api.hpp`, Mako logger/arguments/utils/time, and thread-local logger state.

## Risks and test signals
Fork and IPC failures are key risks. Signals are ping/stop responses, setup error messages, and destructor wait status.
