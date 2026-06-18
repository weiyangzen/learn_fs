# sources/user-network-fs/rclone/lib/israce/norace.go

Source read signal: reviewed complete local file (9 lines, sha256 0d017c64a7177287).

Purpose: Reports non-race-detector builds.

Important APIs/types/functions: Under the `!race` build tag, exports `const Enabled = false`.

Control flow: No runtime flow.

State and persistence behavior: No state.

Dependencies and integration points: Complements `israce.go` so callers have one import regardless of build mode.

Risks and test signals: Build constraints must remain complementary with the race-tagged file.
