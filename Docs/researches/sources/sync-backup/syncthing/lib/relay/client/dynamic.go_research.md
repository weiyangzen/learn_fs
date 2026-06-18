# sources/sync-backup/syncthing/lib/relay/client/dynamic.go

## Purpose
Implements relay clients that fetch a list of available static relay addresses from an HTTP(S) pool endpoint, order them by latency buckets with randomization, and try them sequentially.

## Important APIs, Types, and Functions
`dynamicClient` embeds `commonClient` and stores pool URL, TLS certificates, timeout, and current `staticClient` under an RW mutex. `newDynamicClient`, `serve`, `Error`, `String`, `URI`, `dynamicAnnouncement`, and `relayAddressesOrder` are the key functions/types.

## Control Flow
`serve` strips the `dynamic+` prefix to make an HTTP(S) URL, requests the pool endpoint, decodes `{"relays":[{"url":...}]}`, parses relay URLs, orders them using `relayAddressesOrder`, and for each candidate constructs a static client, publishes it under lock, serves it until it disconnects or errors, then clears it. If all relays fail, it returns an error. `relayAddressesOrder` measures latency, buckets by 50 ms intervals, shuffles within buckets using secure `rand.Shuffle`, sorts bucket IDs, and flattens the result.

## State and Persistence Behavior
No durable state is written. The current static client pointer is mutable in-memory state used by `Error` and `URI`. Network state includes the HTTP pool request and subsequent static relay connections.

## Dependencies and Integration Points
Depends on `net/http`, JSON decoding, URL parsing, `osutil.GetLatencyForURL`, secure random shuffle, and `staticClient`. It integrates with relay pool infrastructure and the common service wrapper.

## Risks and Edge Cases
The HTTP response status is not checked before JSON decoding. A slow or failing latency probe assigns the relay to a high-latency bucket. `URI` returns nil while no static relay is active, so callers must handle nil. Context cancellation during latency ordering returns nil and causes no relay attempts. Dynamic pools with many relays incur serial latency checks.

## Test Signals
There are no direct tests in this subset. Useful tests would cover pool JSON parsing, unsupported relay URL skipping, latency bucket ordering, context cancellation, and fallback through multiple static relays.
