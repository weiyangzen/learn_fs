# sources/sync-backup/syncthing/lib/relay/client/static.go

## Purpose
Implements a long-running client for a single static relay URI. It connects over TLS, joins the relay, responds to pings, forwards session invitations to consumers, and detects timeout or protocol errors.

## Important APIs, Types, and Functions
`staticClient` embeds `commonClient` and stores URI, TLS config, message/connect timeouts, active TLS connection, and relay token. Important methods are `newStaticClient`, `serve`, `String`, `URI`, `connect`, `disconnect`, and `join`. Helpers include `performHandshakeAndValidation` and `messageReader`.

## Control Flow
`serve` connects, joins, clears deadlines, starts `messageReader`, and loops over messages, reader errors, context cancellation, and a message timeout. Pings are answered with `Pong`; session invitations are sent on the shared invitation channel; unexpected messages return protocol errors. `connect` dials TCP with context timeout, clones TLS config to set SNI when possible, applies a deadline, and validates ALPN plus optional relay ID. `join` sends `JoinRelayRequest` with token and expects success, relay-full, or an error response.

## State and Persistence Behavior
State is the active TLS connection pointer and immutable configuration. No durable state is written. The invitation channel can block message processing if consumers do not receive. `disconnect` closes the connection when serving ends.

## Dependencies and Integration Points
Depends on `dialer`, `osutil`, logging, relay protocol messages, TLS ALPN `bep-relay`, and Syncthing device ID derivation from relay certificates. It is used directly by `NewClient` for `relay://` URIs and by dynamic clients for selected relay addresses.

## Risks and Edge Cases
The message receive branch reads from an unbuffered `messages` channel without checking channel close; `messageReader` sends errors separately. Timeout handling depends on resetting the timer correctly. TLS uses `InsecureSkipVerify` from `configForCerts`; optional relay ID validation must be used when identity matters. Invitation delivery can block if no receiver is active.

## Test Signals
No direct tests in this subset. Useful coverage would include ping/pong, invitation forwarding, relay-full join, wrong token response, ALPN mismatch, relay ID mismatch, context cancellation, and idle timeout.
