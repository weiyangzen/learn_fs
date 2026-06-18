# sources/storage-engines/foundationdb/flow/Hostname.cpp

## Purpose
Parses host/service TLS endpoint strings, distinguishes hostnames from numeric IP addresses, and resolves hostnames through Flow network DNS-cache APIs.

## Important APIs, Types, And Functions
`Hostname::isHostname()`, `Hostname::parse()`, `Hostname::resolve()`, `Hostname::resolveWithRetry()`, and `Hostname::resolveBlocking()` are the public behaviors. Internal `resolveImpl()` and `resolveWithRetryImpl()` implement actor-based resolution and retry backoff.

## Control Flow
Parsing rejects empty or non-hostname strings, strips optional `:tls`, splits at the first colon, and constructs `Hostname(host, service, isTLS)`. Async and blocking resolution call DNS-cache APIs, pick one address, clear parsed flags to public, mark `fromHostname`, and restore TLS flag when requested. Retry loops delay with exponential backoff bounded by `FLOW_KNOBS`.

## State And Persistence Behavior
No durable state. DNS cache state lives in `INetworkConnections`. Returned `NetworkAddress` values carry derived flags.

## Dependencies And Integration Points
Depends on `Hostname.h`, regex, `IConnection`, `UnitTest`, `INetworkConnections`, `NetworkAddress`, `FLOW_KNOBS`, actors, and timeout/delay machinery.

## Risks And Edge Cases
Regex validation excludes IPv4/IPv6 numeric addresses by design. Regex exceptions are converted to `address_parse_error`. `resolveWithRetry()` loops forever until success or cancellation, so callers need timeout/cancellation when resolution may never succeed.

## Test Signals
`/flow/Hostname/parse` checks accepted hostname forms, rejected IP/plain-port forms, TLS suffix handling, unresolved `.invalid` behavior, blocking/async optional failure, and timeout of retry resolution.
