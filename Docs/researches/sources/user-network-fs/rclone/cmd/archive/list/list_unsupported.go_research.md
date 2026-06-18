# sources/user-network-fs/rclone/cmd/archive/list/list_unsupported.go

Purpose: Plan 9 build stub for `cmd/archive/list`, keeping the package buildable when list support is excluded with the real archive implementation.

No APIs, state, or runtime flow exist here. Dependency is build tag selection. Risk is intentional command absence on Plan 9. Test signal is platform build success.
