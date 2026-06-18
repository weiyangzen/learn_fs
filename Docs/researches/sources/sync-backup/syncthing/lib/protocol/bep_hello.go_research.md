## sources/sync-backup/syncthing/lib/protocol/bep_hello.go

Purpose: implements BEP hello message serialization, exchange, and version-mismatch detection.

Important APIs: constants `HelloMessageMagic` and `Version13HelloMagic`; errors `ErrTooOldVersion` and `ErrUnknownMagic`; `Hello` with `toWire`, `helloFromWire`, `Magic`; `ExchangeHello`, `IsVersionMismatch`, `readHello`, and `writeHello`.

Control flow and state: `ExchangeHello` requires a non-zero outgoing timestamp, writes a hello, then reads the peer hello. `readHello` reads four magic bytes, handles v0.14 protobuf hello with a two-byte size capped at 32767, maps known old v12/v13 headers to `ErrTooOldVersion`, and otherwise returns `ErrUnknownMagic`. `writeHello` marshals protobuf and panics if too large for the signed 16-bit-compatible size limit.

Dependencies and integration points: used at connection startup before BEP message exchange. Relies on generated `bep.Hello` and protobuf encoding.

Risks: write-before-read ordering assumes both peers follow the same exchange pattern over full-duplex connections. Unknown magic may represent newer protocols or non-Syncthing traffic. Panics on missing timestamp or oversized outgoing hello catch programmer bugs.

Test signals: `bep_hello_test.go` covers current hello parsing and old/unknown magic errors.
