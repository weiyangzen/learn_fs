# sources/storage-engines/foundationdb/fdbclient/ProxyLoadBalance.h

## Purpose
`ProxyLoadBalance.h` provides coroutine helpers for sending requests to commit proxies and GRV proxies while retrying if the database proxy set changes before a reply arrives. It wraps `basicLoadBalance` with proxy-change awareness.

## Important APIs, Types, and Functions
- `ReqBuilder<Req, Args...>` stores constructor arguments and rebuilds a fresh request for every retry.
- `makeReqBuilder<Req>(Args&&...)` decays and validates constructor argument types with `std::is_constructible_v`.
- `commitProxyLoadBalance` takes a commit-proxy channel pointer, optional provisional proxy selection, task priority, and `AtMostOnce` setting.
- The overload without explicit provisional/task parameters uses non-provisional proxies and `cx->taskID`.
- `grvProxyLoadBalance` mirrors the pattern for `GrvProxyInterface`.

## Control Flow and State
Each load-balancer function loops forever until a reply wins a `race` against `cx->onProxiesChanged()`. If the reply wins, it returns the reply. If the proxy-change future wins, it discards the in-flight result and rebuilds the request for the new proxy set.

## State and Persistence Behavior
The helpers keep only local request-builder state. They do not persist or mutate database state directly. `AtMostOnce` is passed through to `basicLoadBalance`, so callers must choose retry semantics suitable for idempotent or non-idempotent requests.

## Dependencies and Integration Points
The file depends on commit/GRV proxy interfaces, `NativeAPI.actor.h` for `Database`, and `fdbrpc/LoadBalance.actor.h` for `basicLoadBalance`. It is a template header so callers get strongly typed request and reply inference through `REPLY_TYPE(Req)`.

## Risks and Edge Cases
- Retrying on proxy changes can duplicate requests unless the channel semantics and `AtMostOnce` choice are correct.
- The request builder assumes constructor arguments are safe to store and reuse. Mutable references should be avoided because arguments are decayed and captured by value.
- A constantly changing proxy set can starve the reply path.

## Test Signals
Tests should simulate proxy-change races, request reconstruction on retry, provisional commit proxy selection, GRV proxy calls, and `AtMostOnce` behavior for requests where duplicate delivery would be harmful.
