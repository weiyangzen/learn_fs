# sources/object-store/garage/src/garage/tests/k2v_client/simple.rs

Purpose: These tests verify that the public `k2v-client` crate works against a live Garage K2V endpoint, including Unicode/special-character key encoding.

Important APIs and types: `test_simple` and `test_special_chars` use `K2vClient`, `K2vValue`, `BatchReadOp`, `Default` filters, and `Context::k2v_client`.

Control flow: The simple test inserts one item with `insert_item`, reads it with `read_item`, and checks a single binary value. The special-character test inserts under partition key `root@plépp` and sort key `≤≤««`, reads it back, waits briefly for index visibility, reads the index to confirm the partition key, and performs a batch read to confirm the sort key.

State and persistence behavior: The tests persist K2V items through the typed client rather than raw HTTP. They validate percent-encoding of non-ASCII/reserved characters and index/batch-read visibility.

Dependencies and integration points: They integrate the `k2v-client` library, Garage K2V API, signed HTTP transport, test bucket permissions, and index maintenance.

Risks: The special-character test sleeps one second before reading the index, indicating asynchronous index propagation. It checks only one value and one batch operation, so broader client behavior is covered by library code and raw K2V tests.

Test signals: Successful insert/read, exact `K2vValue::Value`, index containing the Unicode partition key, and batch read containing the Unicode sort key.
