# sources/storage-engines/foundationdb/fdbserver/ratekeeper/include/fdbserver/ratekeeper/Ratekeeper.h

Purpose: exposes the public entry point for starting a ratekeeper actor from other fdbserver modules.

Important APIs and functions: declares `Future<Void> ratekeeper(RatekeeperInterface rkInterf, Reference<AsyncVar<ServerDBInfo> const> dbInfo)`. It forward-declares `ServerDBInfo` and includes `RatekeeperInterface` plus Flow primitives.

Control flow, state, and persistence: none in the header. The returned actor is implemented by `Ratekeeper::run` and owns all runtime monitoring, system-key watches, and rate computation.

Dependencies and integration: this is the public include path exported by the ratekeeper CMake target. Recruitment or role-startup code can include it without depending on internal `Ratekeeper.h` implementation details.

Risks and test signals: risks are ABI/API mismatch if the internal signature changes without this wrapper. Build/link tests should ensure consumers can include this header and link against `fdbserver_ratekeeper`.
