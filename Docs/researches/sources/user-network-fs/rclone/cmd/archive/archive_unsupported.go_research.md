# sources/user-network-fs/rclone/cmd/archive/archive_unsupported.go

Purpose: Plan 9 build stub for the archive root package. It prevents "no buildable Go source files" on unsupported platforms while excluding archive functionality there.

There are no functions, state changes, or runtime control flow. Dependency is only the Go build tag `plan9`. Risk is that Plan 9 builds compile without registering the archive command, which is intentional given archive dependencies. Test signal is platform build success.
