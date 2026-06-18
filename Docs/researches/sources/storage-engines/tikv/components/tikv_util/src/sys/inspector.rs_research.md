# sources/storage-engines/tikv/components/tikv_util/src/sys/inspector.rs

## Purpose
Defines a platform abstraction for inspecting current-thread IO and disk-device statistics, with a Linux `/proc` implementation and no-op fallback elsewhere.

## Important APIs, Types, and Functions
- `IoStat { read, write }` and `DiskStat` mirror process IO and diskstat fields.
- `ThreadInspector` trait exposes `io_stat`, `get_device`, and `disk_stat`.
- Linux `ThreadInspectorImpl` wraps `procfs::process::Process` rooted at `/proc/<pid>/task/<tid>`.
- Linux helpers convert `procfs::process::Io` and `procfs::DiskStat`, identify device major/minor with `fstat`, and scan `/proc/diskstats`.
- `self_thread_inspector()` constructs an inspector for the current thread.

## Control Flow
On Linux, current process/thread IDs are used to create a procfs `Process` rooted at the task directory. `io_stat` reads task IO counters. `get_device` opens a path and uses `fstat` to determine device major/minor. `disk_stat` reads and parses `/proc/diskstats`, returning the matching device entry.

## State and Persistence Behavior
Inspector instances hold a procfs process handle/root. Each stat query reads current kernel state. No persistent state is written.

## Dependencies and Integration Points
Depends on `procfs`, `libc`, and `crate::sys::thread`. The abstraction lets code collect backend IO and disk stats where supported while compiling elsewhere.

## Risks
Linux implementation relies on procfs format and permissions. `disk_stat` returns an error if any line parsing fails before a match, which can make malformed unrelated lines fatal. Device identification opens the target path and can fail for missing/inaccessible paths.

## Test Signals
Linux tests verify current-thread IO write delta after syncing a temporary file and confirm disk stats can be found for the current directory's device.
