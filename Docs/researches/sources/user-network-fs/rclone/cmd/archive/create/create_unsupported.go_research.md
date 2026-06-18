# sources/user-network-fs/rclone/cmd/archive/create/create_unsupported.go

Purpose: Plan 9 build stub for `cmd/archive/create`, keeping the package buildable when the real archive create implementation is excluded.

There is no runtime behavior. State is limited to build selection via `//go:build plan9`. Dependencies are none beyond package identity. Risk is intentional absence of the create subcommand on Plan 9. Test signal is platform compile success.
