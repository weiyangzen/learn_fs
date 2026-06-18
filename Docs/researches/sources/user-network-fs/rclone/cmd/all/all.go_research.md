# sources/user-network-fs/rclone/cmd/all/all.go

Purpose: aggregate import package that registers all active rclone commands by blank-importing each command package. Importing `cmd/all` gives a complete CLI command tree through each package's `init` registration.

Control flow is entirely Go import side effects; there are no functions. State mutation happens through command registration into the root Cobra command and any package-level flag variables initialized by imported packages. Dependencies are every listed command package. Risks include missing a new command from this list, importing platform-specific packages with build constraints, and global initialization order/side effects. Test signal is build coverage: if any imported command fails to compile, the aggregate package fails.
