# sources/user-network-fs/rclone/vfs/vfstest/dir_non_unix.go

## Purpose
Provides the non-Unix fallback for the directory rewind test.

## APIs, Flow, And State
`TestDirRewind` simply skips with the current `runtime.GOOS`. It has no persistent state.

## Dependencies And Integration
Selected outside Linux, Darwin, and FreeBSD so the package still exposes a `TestDirRewind` symbol without raw `getdents` dependencies.

## Risks And Test Signals
The skip means directory stream rewind behavior is untested on these platforms. The useful signal is that unsupported builds compile cleanly and report an explicit skip.
