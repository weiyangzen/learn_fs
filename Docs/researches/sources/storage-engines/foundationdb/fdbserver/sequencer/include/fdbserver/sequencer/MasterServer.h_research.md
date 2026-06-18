# sources/storage-engines/foundationdb/fdbserver/sequencer/include/fdbserver/sequencer/MasterServer.h

Purpose: exposes the public master/sequencer role actor entry point.

Important APIs and functions: declares `Future<Void> masterServer(MasterInterface mi, Reference<AsyncVar<ServerDBInfo> const> db, Reference<AsyncVar<Optional<ClusterControllerFullInterface>> const> ccInterface, ServerCoordinators serverCoordinators, LifetimeToken lifetime, bool forceRecovery)`.

Control flow, state, and persistence: none in the header. The implementation waits for cluster-controller alignment, constructs `MasterData`, serves version and live-committed-version endpoints, accepts recovery data, and terminates on lifetime replacement.

Dependencies and integration: includes coordination and master interfaces plus Flow primitives; forward-declares cluster-controller and server DB info. Exported through the sequencer library public include path.

Risks and test signals: risks are public signature drift and missing forward declarations. Link tests and role recruitment compilation are the key signals.
