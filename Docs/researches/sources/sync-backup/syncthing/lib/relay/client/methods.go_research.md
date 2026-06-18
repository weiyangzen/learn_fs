# sources/sync-backup/syncthing/lib/relay/client/methods.go

## Purpose
Implements one-shot relay client operations: request a session invitation from a relay, join a relay session, test a relay repeatedly, and construct TLS configs from local certificates.

## Important APIs, Types, and Functions
`incorrectResponseCodeErr` formats non-success relay responses. `GetInvitationFromRelay` connects to a relay, sends `ConnectRequest`, and waits for `SessionInvitation`. `JoinSession` connects to a session invitation's address and sends `JoinSessionRequest`. `TestRelay` repeatedly connects and joins a relay with optional sleeps. `configForCerts` builds a TLS config with relay ALPN and certificate settings.

## Control Flow
`GetInvitationFromRelay` creates a static client, connects and joins the relay, writes a `ConnectRequest` for the target device ID, then reads relay protocol messages until it receives a successful response followed by an invitation, a relay-full/error response, a timeout, or context cancellation. `JoinSession` dials the invitation address, performs TLS handshake with relay protocol ALPN, sends the session key, and either returns the TLS connection or fails on non-success response. `TestRelay` repeats static connect/join attempts, waiting between attempts when requested.

## State and Persistence Behavior
No durable state. Network connections are opened, deadlines set, and returned or closed depending on success. TLS config includes certificates and disables certificate verification, relying instead on protocol-level relay ID validation when requested elsewhere.

## Dependencies and Integration Points
Depends on context, TLS, net/url, dialer, relay protocol packets, Syncthing device IDs, and static client helpers. It integrates with relay discovery/connection management and NAT traversal session establishment.

## Risks and Edge Cases
`InsecureSkipVerify` is intentional for relay protocol but requires compensating validation when an expected relay ID is supplied. Timeouts and deadlines must be reset or set carefully to avoid hanging. Invitation flow assumes response-before-invitation ordering. Returned `net.Conn` from `JoinSession` transfers close responsibility to the caller.

## Test Signals
No direct tests in this subset. Strong tests would simulate relay protocol sequences, unexpected message types, wrong response codes, relay-full responses, context cancellation, and TLS protocol negotiation failures.
