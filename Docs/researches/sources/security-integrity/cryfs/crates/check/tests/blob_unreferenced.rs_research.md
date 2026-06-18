## sources/security-integrity/cryfs/crates/check/tests/blob_unreferenced.rs

Purpose: constructs blobs that exist in the blockstore but have no directory-entry reference from the filesystem root, then verifies that their root data nodes are reported as unreferenced.

Important APIs and functions: `make_single_node_file_blob`, `make_large_file_blob`, `make_single_node_dir_blob`, `make_large_dir_blob`, `make_single_node_symlink_blob`, and `make_large_symlink_blob` create orphan blobs of all blob types and sizes. `make_dir_blob_with_children` creates an unreferenced directory with child entries. Local `parent_id`, `blob_id`, and `data` generate deterministic ids and payloads.

Control flow and state: helper functions use `update_fsblobstore` to create blobs with a fake parent id that is never linked into the root tree. Large helpers write enough data or entries to force multi-node data trees and compute expected root `NodeInfoAsSeenByLookingAtNode` via `DataTree::into_root_node`. The directory-with-children case also gathers descendant blob ids and expects their root nodes to be unreferenced.

Dependencies and integration: uses low-level `BlobOnBlocks`, `DataTree`, `FsBlob::into_raw`, fsblobstore creation APIs, UID/GID/mode metadata, and common descendant expectation helpers. It validates that the checker’s reachability phase starts from root directory references, not from the blobstore inventory alone.

Risks and test signals: coverage spans file, directory, and symlink root-node shapes, including single-leaf and inner-root trees. The risk is sensitivity to constants that force large-node fanout; assertions fail loudly if fixture sizes stop producing enough nodes.
