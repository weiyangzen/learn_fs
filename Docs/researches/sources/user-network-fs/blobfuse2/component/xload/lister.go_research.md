## sources/user-network-fs/blobfuse2/component/xload/lister.go

Purpose: Implements the xload directory enumeration stage. It lists the remote namespace, creates matching local directories, and schedules files for the splitter.

Important APIs and flow: `newRemoteLister` validates path, workers, remote, and stats, initializes a thread pool, and stores default permissions. `Start` begins workers and schedules an initial empty-path list. `Process` optionally waits for `azstorage.block-list-on-mount-sec` once, then repeatedly calls `remote.StreamDir` with continuation tokens. Directory entries trigger asynchronous `mkdir` plus recursive schedule; file entries schedule `WorkItem`s on the next component with size, mode, timestamps, and MD5. `mkdir` uses `os.MkdirAll` and reports lister stats.

State and dependencies: Uses `listBlocked` to ensure the configured initial list delay runs once, and uses the downstream `XComponent` chain for file processing. It depends on `config`, `internal.StreamDirOptions`, stats, and local filesystem permissions.

Risks: Directory creation goroutines capture and assign `err` from the outer scope, which is race-prone. Recursive scheduling can continue after `Stop` if goroutines are still running. Tests cover construction, start/stop listing against loopback, and mkdir.
