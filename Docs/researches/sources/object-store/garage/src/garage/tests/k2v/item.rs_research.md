# sources/object-store/garage/src/garage/tests/k2v/item.rs

Purpose: This file tests individual K2V item semantics and index counters, plus response content negotiation for single values, conflicts, and tombstones.

Important APIs and types: `test_items_and_indices` and `test_item_return_format` use `CustomRequester`, causality headers, `ReadIndex`, base64 JSON values, Hyper status/content types, and `assert_json_eq`. `test_items_and_indices` is marked ignored as flaky.

Control flow: The ignored index test writes values for sort keys `a` through `d`, reads tokens, checks partition index counters after each write, overwrites with causality, creates concurrent values using stale causality, verifies conflict JSON output, then deletes each key and checks counters shrink. `test_item_return_format` writes a single value, reads it with `*/*`, no Accept, binary Accept, and JSON Accept; then creates a concurrent value and tests conflict behavior; then creates a concurrent tombstone and finally deletes everything.

State and persistence behavior: The tests validate K2V's causal value set: single values, concurrent values, tombstones, and causality tokens. Index state tracks entries, conflicts, values, and bytes. Response state changes based on Accept headers: binary for single values, JSON arrays for conflicts or unspecified/json accept, 409 for binary conflict, 204 for no-content binary/tombstone cases.

Dependencies and integration points: They exercise K2V table storage, index maintenance, causality resolution, content negotiation, and async visibility of index updates.

Risks: The main index test is ignored because it is flaky and includes sleeps, indicating eventual index update timing or background propagation sensitivity. Exact byte counters and JSON ordering are brittle to implementation changes.

Test signals: Exact content types, causality-token presence, response statuses 200/204/409, value arrays with base64 or null entries, and partition index counters after writes/deletes.
