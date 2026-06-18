# sources/user-network-fs/mergerfs/src/state.hpp

## Purpose
Declares the central process state object for open-file tracking and runtime get/set control handlers.

## Important APIs, Types, and Functions
`State::OpenFile` records `ref_count`, `backing_id`, and `FileInfo*` in a `boost::concurrent_flat_map`. `get_fi()` resolves a `FileInfo` from a FUSE file handle or by nodeid lookup. `GetSet` stores getter, setter, and validator callbacks.

## Control Flow
`get_fi()` first tries `FileInfo::from_fh(fh_)`; if absent it visits `open_files` for `ctx_->nodeid` and returns the stored pointer. The `OpenFile` move constructor uses relaxed atomic loading because insertion is not yet observable.

## State and Persistence Behavior
`open_files` is process-live state for open backing files. `_getset` stores runtime control callbacks. No persistent storage exists beyond backing files handled elsewhere.

## Dependencies and Integration Points
Includes Boost concurrent containers, FUSE request context, `fileinfo.hpp`, and callback machinery. FUSE operations use this to route fd-based operations after unlink or when file handles are encoded differently.

## Risks and Edge Cases
Fallback by nodeid can return a `FileInfo` when `fh` is not directly decodable, so nodeid lifecycle correctness is critical. Callback map access is not shown as concurrent-safe.

## Test Signals
Open-after-unlink tests, concurrent open/release tests, get/set xattr tests, and nodeid/fh fallback coverage are key.
