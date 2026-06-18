# sources/storage-engines/foundationdb/fdbserver/commitproxy/include/fdbserver/commitproxy/CommitProxyServer.h

## Purpose
This public include is the narrow module boundary for starting a commit proxy actor. It hides the large `CommitProxyServer.cpp` implementation and exposes only the `commitProxyServer` coroutine signature needed by worker recruitment code.

## Important API
`Future<Void> commitProxyServer(CommitProxyInterface proxy, InitializeCommitProxyRequest req, Reference<AsyncVar<ServerDBInfo> const> db, std::string whitelistBinPaths)` starts and supervises the commit proxy role. The inputs provide the role's network interface, master initialization request, changing database information, and snapshot-command binary whitelist string. The function returns normally only when handled termination conditions are swallowed in the implementation; unexpected errors are rethrown.

## Control flow and state
The header declares no state and performs no logic. Its main design decision is to forward declare `InitializeCommitProxyRequest` and `ServerDBInfo`, reducing include coupling for callers. Runtime state is owned entirely by `CommitProxyServerCore` and `ProxyCommitData` in the implementation file.

## Dependencies and integration points
The header includes `fdbclient/CommitProxyInterface.h` for the role interface and `flow/flow.h` for `Future`, `Reference`, and `AsyncVar`. It is included by server-role wiring that recruits commit proxies during recovery and passes live `ServerDBInfo` updates.

## Risks and test signals
The API is intentionally small, so the primary risk is signature drift between declaration and implementation. The implementation matches this declaration. Link tests for the commitproxy library and any server recruitment tests should catch missing symbols or include dependency regressions. Behavior-level tests are in the implementation's simulation workload coverage, not in this header.
