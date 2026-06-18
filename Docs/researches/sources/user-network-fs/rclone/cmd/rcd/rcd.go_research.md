# sources/user-network-fs/rclone/cmd/rcd/rcd.go

Purpose: implements `rclone rcd`, running rclone as an RC server.

Important API: Cobra command registered on root; delegates to rclone RC server startup helpers and config flags. It is the daemon/server complement to `rclone rc`.

Control flow: validates no path args, enables RC serving configuration, and enters the RC server lifecycle through shared command/run infrastructure. It typically blocks serving requests until interrupted.

State/persistence: process-local HTTP server state; endpoints may mutate remotes/config depending on enabled RC calls. Dependencies include rc flags/server packages and command lifecycle. Risks include exposed unauthenticated control API if configured unsafely and long-running process cleanup. Test signal likely in rc server tests.
