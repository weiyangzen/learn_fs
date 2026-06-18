## sources/sync-backup/syncthing/lib/protocol/bep_hello_test.go

Purpose: tests BEP hello exchange compatibility and error classification.

Important tests/helpers: `TestVersion14Hello` builds a v0.14 hello frame, exchanges it through an in-memory `readWriter`, and verifies received fields. `TestOldHelloMsgs` feeds known v12, v13, and unknown magic headers and checks exact errors. `readWriter` couples separate reader/writer buffers for `ExchangeHello`.

Control flow and state: tests simulate the peer's read side with prepared bytes while capturing outgoing write bytes.

Dependencies and integration points: validates protobuf hello framing used before connection startup.

Risks: does not test oversized messages, missing timestamp panic, short reads, or malformed protobuf bodies.

Test signals: focused compatibility coverage for hello framing.
