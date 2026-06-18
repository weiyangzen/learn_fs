# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributor.h

Purpose: declares the real data distributor actor entry point.

Important APIs and functions: `Future<Void> dataDistributor(DataDistributorInterface ddi, Reference<AsyncVar<ServerDBInfo> const> db, std::string folder)` starts the DD role using its RPC interface, live server DB info, and data folder.

Control flow: implementation is not in this header. Callers hand the actor a `DataDistributorInterface`; the actor is expected to initialize DD state, participate in leader/role lifecycle, and run until cancellation or error.

State and persistence: no local state. The actor implementation will use `ServerDBInfo`, system keys, move-key locks, and DD components declared elsewhere.

Dependencies and integration: includes `DataDistributorInterface` and Flow. Forward-declares `ServerDBInfo`. This is the public include for fdbserver role startup.

Risks: minimal header risk, but signature changes would affect role startup call sites. The `folder` parameter couples actor startup to local process storage/log paths.

Test signals: compile/link coverage and role startup simulation tests should ensure the actor can be constructed with the current interface.
