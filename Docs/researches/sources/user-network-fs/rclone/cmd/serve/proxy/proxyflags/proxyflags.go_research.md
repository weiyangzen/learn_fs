<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go

Source read: complete file, 13 lines, 386 bytes, sha256 `38e3d42a240745fe7fd68204a73e35a11a44ed232d68937663d7370955d6674f`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go_research.md`.

## Purpose
Adds auth-proxy command-line flags to serve subcommands that support dynamic backend selection.

## Important APIs, types, and functions
`AddFlags` calls `flags.AddFlagsFromOptions` with `proxy.OptionsInfo` and no prefix.

## Control flow
Serve commands call this during init, causing Cobra/pflag to expose `--auth-proxy` on those commands.

## State and persistence behavior
No state beyond binding command-line values into global proxy options.

## Dependencies and integration points
Depends on `cmd/serve/proxy`, rclone flag helpers, and `pflag`.

## Risks and edge cases
Any subcommand using it shares the same unprefixed flag name, so registration order and global options must stay consistent.

## Test signals
Covered indirectly by serve command construction and auth-proxy integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go -->
