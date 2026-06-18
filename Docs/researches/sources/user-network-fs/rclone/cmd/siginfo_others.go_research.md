<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_others.go -->
# sources/user-network-fs/rclone/cmd/siginfo_others.go

Source read: complete file, 7 lines, 150 bytes, sha256 `bbc2173a42d691d7758d030225eb9989152942c8c5e777d5060a0192f9576cd4`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/siginfo_others.go_research.md`.

## Purpose
Provides a no-op SIGINFO handler for non-BSD platforms.

## Important APIs, types, and functions
`SigInfoHandler` is an empty function under the inverse build tag.

## Control flow
No control flow.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends only on build constraints matching the BSD implementation.

## Risks and edge cases
Users on these platforms do not get SIGINFO stats behavior through this hook.

## Test signals
Build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_others.go -->
