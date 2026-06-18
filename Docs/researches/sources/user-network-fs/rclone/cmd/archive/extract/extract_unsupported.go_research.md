# sources/user-network-fs/rclone/cmd/archive/extract/extract_unsupported.go

Purpose: Plan 9 build stub for `cmd/archive/extract`, keeping the package buildable when extraction support is excluded.

There are no functions or runtime state. Dependency is the `plan9` build tag. Risk is intentional absence of the extract subcommand on Plan 9. Test signal is build success on unsupported platform targets.
