# sources/storage-engines/rocksdb/util/coro_utils.h

Purpose: supplies macros that let RocksDB declare and define paired synchronous and coroutine implementations from mostly shared code, while compiling cleanly when coroutine support is disabled.

Important APIs and macros: with `USE_COROUTINES`, `DECLARE_SYNC_AND_ASYNC`, `DECLARE_SYNC_AND_ASYNC_OVERRIDE`, and `DECLARE_SYNC_AND_ASYNC_CONST` declare both the regular function and a `folly::coro::Task<ret>` function with `Coroutine` suffix. Without coroutine support, they declare only the synchronous function. `using_coroutines()` is a constexpr feature probe. The second section undefines and redefines `DEFINE_SYNC_AND_ASYNC`, `CO_AWAIT`, and `CO_RETURN` based on whether the current inclusion is for `WITH_COROUTINES` or `WITHOUT_COROUTINES`.

Control flow and inclusion model: the file intentionally has a guarded declaration section and an unguarded idempotent macro-definition section. A source file can include it once normally, then include sync-and-async implementation headers twice with `WITH_COROUTINES` and `WITHOUT_COROUTINES` to generate both function bodies. In coroutine mode, `CO_AWAIT(foo)` expands to `co_await fooCoroutine`; in synchronous mode it expands to `foo`.

State and persistence: no runtime state or persistence. The behavior is entirely compile-time macro expansion.

Dependencies and integration points: conditionally includes Folly coroutine headers. Used by table cache, block based table reader, and version set sync/async implementation headers to keep MultiGet-style logic shared across sync and async variants.

Risks: macro hygiene is central; callers must define exactly the intended `WITH_COROUTINES` or `WITHOUT_COROUTINES` mode before including shared implementation fragments. Typos in the header comments do not affect behavior, but macro misuse can silently generate missing declarations or wrong call forms. The file lacks `#pragma once` around the whole file by design, so maintainers must preserve the two-section structure.

Test signals: indirect coverage comes from builds with and without `USE_COROUTINES` and tests exercising sync/async table read paths. There is no local runtime test because the utility is preprocessor-only.
