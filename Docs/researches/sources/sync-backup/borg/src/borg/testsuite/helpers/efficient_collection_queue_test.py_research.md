# sources/sync-backup/borg/src/borg/testsuite/helpers/efficient_collection_queue_test.py

Purpose: verifies `EfficientCollectionQueue` behavior for byte and list collections with bounded front chunks.

Important APIs and control flow: tests create queues with chunk size and collection factory, inspect empty `peek_front`, push data, check total length and truthiness, pop exact sizes, verify chunk-boundary behavior, and require `SizeUnderflow` when popping more than available.

State and persistence: in-memory queue state tracks appended chunks, total length, and front consumption.

Dependencies and integration points: depends on `helpers.datastruct.EfficientCollectionQueue`. It supports stream assembly/consumption code that needs efficient front slicing without repeatedly copying whole buffers.

Risks: semantics differ by collection type (`bytes` empty value versus `list` empty value). Underflow must leave remaining data intact.

Test signals: expected front slices, length/truthiness transitions, and underflow exception while preserving queued tail.
