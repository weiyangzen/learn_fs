## sources/security-integrity/cryfs/crates/check/tests/node_unreadable.rs

Purpose: verifies `NodeUnreadableError` reporting when node blocks exist but fail to decode or pass integrity, and validates secondary effects on blob readability and descendant reachability.

Important APIs and functions: tests cover unreadable single-node blobs, root directory single-node without children, unreadable root nodes, unreadable inner nodes, unreadable leaf nodes, and multiple corrupted nodes. They use fixture corruption methods that flip bytes in stored blocks while preserving expected reference metadata.

Control flow and state: each test prepares a blob, records descendant blobs when target is a directory, corrupts selected node blocks, builds expected `NodeUnreadableError`s plus `BlobUnreadableError` for affected blobs and `NodeUnreferencedError`s for orphaned children, runs the checker, and compares unordered.

Dependencies and integration: depends on `BlobReference`, `BlobReferenceWithId`, `BlobUnreadableError`, `NodeUnreadableError`, `BlobType`, and common helpers. It exercises the blockstore integrity layer through actual encrypted block corruption rather than mocking decode failures.

Risks and test signals: directory blobs produce extra unreadable blob errors because checker traversal attempts to decode them as filesystem directories. The multi-corruption case is a strong signal for de-duplicating references and handling unreachable child references after corrupted ancestors.
