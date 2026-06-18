# sources/object-store/garage/src/garage/tests/k2v/poll.rs

Purpose: This file contains K2V long-polling integration tests for individual items and ranges. Both tests are currently ignored as broken.

Important APIs and types: `test_poll_item` uses GET with `causality_token` and `timeout`. `test_poll_range` uses POST with `poll_range`, `seenMarker`, and range response JSON. They use `tokio::spawn`, `tokio::select!`, `Duration`, base64 JSON assertions, and causality headers.

Control flow: The item test writes an initial value, reads its causality token, starts a polling request waiting for changes, writes a superseding value with that token, and expects the poll to return the new body before timeout. The range test writes an initial value, obtains a seen marker from `poll_range`, starts a second poll with that marker, writes an updated value, expects one changed item, then repeats with a second sort key.

State and persistence behavior: The intended behavior is that K2V stores seen markers and causality tokens sufficient for blocking until a newer value appears. Poll responses include changed items and updated markers.

Dependencies and integration points: These tests exercise K2V's notification/waiting path, request timeout handling, causal item updates, and range-change detection.

Risks: Both tests are ignored with "currently broken", so they document desired behavior but are not active regression guards. They use 10-second timeout races and spawned tasks, so even when enabled they are timing-sensitive.

Test signals: If re-enabled, signals would be poll completion before timeout, 200 status, expected binary/JSON bodies, and marker progression across changes.
