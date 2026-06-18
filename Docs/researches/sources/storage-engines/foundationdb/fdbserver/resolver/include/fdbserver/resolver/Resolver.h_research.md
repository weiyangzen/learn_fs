# sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/Resolver.h

Purpose: exposes the public resolver role entry point to the rest of fdbserver.

Important APIs and functions: declares `Future<Void> resolver(ResolverInterface resolver, InitializeResolverRequest initReq, Reference<AsyncVar<ServerDBInfo> const> db)`. It forward-declares initialization and DB info types and includes the resolver interface plus Flow primitives.

Control flow, state, and persistence: none in the header. Runtime behavior lives in `resolverCore` and the wrapper `resolver` in `Resolver.cpp`, including optional logsystem-backed state store setup.

Dependencies and integration: exported through the resolver library's public include directory. Role recruitment code can call this actor without seeing conflict-set internals.

Risks and test signals: risks are public signature drift and missing includes for consumers. Link tests and role startup tests should compile this header and instantiate the resolver actor through the built target.
