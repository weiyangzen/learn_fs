# sources/object-store/garage/src/table/merkle.rs

Purpose: maintains per-table Merkle trees used by anti-entropy synchronization. Data is split into 2^16 Merkle partitions based on partition-key hash prefixes.

Important APIs and types: `MerkleUpdater<F, R>` owns `TableData` and the empty-node hash. `MerkleNodeKey` identifies a partition and hash prefix. `MerkleNode` is `Empty`, `Intermediate(Vec<(u8, Hash)>)`, or `Leaf(key, value_hash)`. Methods include `new`, `spawn_workers`, `update_item`, recursive `update_item_rec`, `read_node`, and approximate length helpers.

Control flow: the worker reads the first `merkle_todo` entry, computes the full table-key hash, maps the partition through replication, recursively updates the tree, then removes the todo only if it still equals the processed value hash. Recursion collapses empty/single-child intermediates, splits leaf collisions into deeper prefixes, and stores non-empty nodes as nonversioned-encoded blobs whose hashes form parent entries. Work is batched in `spawn_blocking` for up to 100 updates per iteration.

State and persistence: persistent trees are `merkle_tree` and `merkle_todo`. Empty nodes are implicit by missing DB entries. A todo value is either a value hash or empty bytes for deletion.

Dependencies and integration: used by `TableSyncer` for root/node comparisons and by `TableData` mutations through Merkle todos. Depends on Garage DB transactions, layout partitions, nonversioned encoding, background workers, and Tokio notifications.

Risks and test signals: Merkle lag is tolerated and logged during sync. Recursive collision handling and ordered intermediate children are correctness-sensitive. There is a direct unit test for intermediate child insert/remove ordering, but full tree update behavior is integration-tested.
