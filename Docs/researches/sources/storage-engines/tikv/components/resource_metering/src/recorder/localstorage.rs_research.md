# sources/storage-engines/tikv/components/resource_metering/src/recorder/localstorage.rs

## Purpose
`localstorage.rs` defines the thread-local storage used by resource metering to associate currently polled work with a resource tag and per-thread summary counters.

## Important APIs, Types, And Functions
`STORAGE` is a thread-local `RefCell<LocalStorage>`. `LocalStorage` tracks registration status, failed register attempts, whether a tag is currently set, the shared attached tag, whether summaries are enabled, current summary record, and a shared map of summary records keyed by `Arc<TagInfos>`.

`LocalStorageRef` packages a thread `Pid` with a clone of its `LocalStorage` for recorder registration. `SharedTagInfos` wraps `Arc<AtomicCell<Option<Arc<TagInfos>>>>` and provides `new`, `swap`, and `load_full`. `load_full` temporarily swaps the tag out, clones it, then restores it.

## Control Flow
`ResourceMeteringTag::attach` mutates the thread-local `LocalStorage`, and the recorder registers `LocalStorageRef`s so background sampling can inspect per-thread tags and summaries. `Guard::drop` clears the tag and merges summaries through the same storage.

## State And Persistence Behavior
State is thread-local plus shared `Arc` fields cloned into recorder-visible references. Summary maps are protected by `Mutex`; tag access is lock-free through `AtomicCell<Option<Arc<TagInfos>>>`. Nothing is persisted.

## Dependencies And Integration Points
The file depends on `collections::HashMap`, `crossbeam::atomic::AtomicCell`, `tikv_util::sys::thread::Pid`, `TagInfos`, and `SummaryRecord`. It is a private recorder support module used by `lib.rs` and recorder internals.

## Risks
`SharedTagInfos::load_full` uses swap/restore and asserts that no other value appears during restoration. Misuse outside the expected recorder/guard coordination could panic or cause spinning in `Guard::drop`. Cloning `LocalStorage` shares the summary arcs, so ownership boundaries must be understood by recorder code.

## Test Signals
No local tests, but `lib.rs::test_attach` validates basic attached-tag visibility and cleanup through this storage.
