# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/open_file_list.rs

Purpose: thread-safe registry of open file objects keyed by `FileHandle`.

Important APIs: `OpenFileList::new`, async `get`, `add`, `remove`, test-only `for_each`, `ForEachCallback`, and `AsyncDrop`.

Control flow and state: wraps `HandleMap<FileHandle, AsyncDropArc<OF>>` in a mutex. `get` clones the open-file arc while holding the mutex, releases the mutex before awaiting the callback, then async-drops the clone. `add` stores a new async-drop arc. `remove` removes by handle and returns the guard for final release.

Dependencies and integration: used by both adapters for file I/O. Test cache flush iterates open files and fsyncs them.

Risks and tests: invalid `get` returns `InvalidFileDescriptor`, but invalid `remove` panics through `HandleMap`. AsyncDrop unwraps the inner drop result, so drop failures can panic.
