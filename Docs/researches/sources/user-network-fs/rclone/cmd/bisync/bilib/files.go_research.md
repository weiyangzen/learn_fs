# sources/user-network-fs/rclone/cmd/bisync/bilib/files.go

Purpose: local filesystem utility functions for bisync code/tests. It detects local versus remote-looking paths, checks file existence, copies files preserving mode/mtime, and recursively copies directories while skipping symlinks.

Important APIs: `IsLocalPath`, `FileExists`, `CopyFileIfExists`, `CopyFile`, and `CopyDir`. State changes are local file/directory creation, chmod, and chtimes. Dependencies are OS path semantics and regexes for local, Windows drive, and rclone remote syntax. Risks include remote/local ambiguity (`c:dir` differs by OS), no symlink copying, destination directory must not preexist, and recursive copy stops on first error. Test signal is indirect through bisync tests and debug helpers.
