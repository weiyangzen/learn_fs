# sources/storage-engines/pebble/batchrepr/writer_test.go

## Purpose
This file tests and visualizes in-place batch header writes. It also provides `prettyBinaryRepr`, a helper for readable datadriven output of raw batch bytes.

## Important APIs, Types, And Functions
`TestWriter` supports datadriven commands `init`, `read-header`, `set-count`, and `set-seqnum`. `prettyBinaryRepr` prints the header and each decodable record, falling back to an invalid-remainder line when `Reader.Next` reports corruption.

## Control Flow
The datadriven test maintains one `repr` slice across commands. It initializes from hex input with `readRepr`, mutates header fields with `SetCount` or `SetSeqNum`, then prints the resulting bytes. Pretty-printing delegates record parsing to `Read`/`Reader.Next`.

## State And Persistence Behavior
State is the mutable representation byte slice. The tests confirm header updates happen in place and do not disturb trailing record bytes. This mirrors production mutation of WAL batch headers.

## Dependencies And Integration Points
It depends on `datadriven`, `base.ParseSeqNum`, `binfmt`, and reader helpers from the same package. The helper is test-only but useful for diagnosing binary representation regressions.

## Risks And Edge Cases
The test covers short representations by printing hex instead of decoding. It also preserves invalid record bytes when pretty-printing, reducing the chance that diagnostic output hides corruption.

## Test Signals
Golden datadriven outputs verify endian layout, count offset, sequence-number formatting, and integration with reader decoding.
