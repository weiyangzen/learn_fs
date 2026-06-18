# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StatusClient.h

## Purpose
`StatusClient.h` declares the client entry point for fetching FoundationDB status JSON. It provides a small facade over the actor implementation that queries full or selected status fields from a database.

## Important APIs, Types, And Functions
- `StatusClient::StatusLevel` enumerates minimal, normal, detailed, and JSON status levels.
- `StatusClient::statusFetcher(Database db, std::string statusField = "")` returns `AsyncResult<StatusObject>`.
- The documented `statusField` currently supports empty/full status or `"fault_tolerance"` for a focused subset.

## Control Flow And State
The header only declares the static method. The implementation actor fetches status data from the database and returns a `StatusObject`.

## Persistence And External State
No local state is declared. The result is live cluster status JSON; requests may read from system/status APIs and depend on cluster availability.

## Dependencies And Integration Points
It depends on Flow, `Status.h`, and `DatabaseContext.h`. It integrates with CLI status commands, management APIs, monitoring tools, and any client code that needs cluster status.

## Risks And Edge Cases
Only selected field filtering is documented; arbitrary fields are not supported. Status fetches can be incomplete, timeout, or fail if the cluster/controller is unavailable. Callers need to handle `AsyncResult` errors and incomplete status messages.

## Test Signals
Tests should cover full status fetch, fault-tolerance subset fetch, unsupported field behavior, controller unavailable paths, timeout/incomplete messages, JSON shape validation, and status level use by callers.
