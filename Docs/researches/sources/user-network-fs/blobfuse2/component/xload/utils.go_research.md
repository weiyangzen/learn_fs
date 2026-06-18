## sources/user-network-fs/blobfuse2/component/xload/utils.go

Purpose: Shared constants, work item schema, mode enum, rounding helper, and local file presence probe for xload.

Important APIs and flow: Constants define maximum workers, lister/splitter caps, `MB`, and component names. `WorkItem` carries all data passed between lister, splitter, and data manager: path, size, mode, timestamps, block, file handle, response channel, direction, priority, cancellation context, and MD5. `Mode` uses `JeffreyRichter/enum` to parse and stringify `PRELOAD`, `UPLOAD`, `SYNC`, and `INVALID_MODE`. `RoundFloat` rounds to a fixed precision. `isFilePresent` wraps `os.Stat` and returns presence, directory flag, and size.

State and dependencies: No persistent state. Depends on `os`, `time`, `context`, `math`, enum reflection, and logging.

Risks: `WorkItem` is a broad mutable transport object shared across goroutines; correctness depends on stage conventions. Unsupported modes parse successfully but later fail in xload start. `isFilePresent` logs all stat failures as debug, including permission errors. Tests cover mode parsing/stringing, rounding, and file presence.
