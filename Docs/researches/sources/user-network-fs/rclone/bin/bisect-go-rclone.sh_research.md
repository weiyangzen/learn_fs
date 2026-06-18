# sources/user-network-fs/rclone/bin/bisect-go-rclone.sh

Purpose: example `git bisect run` helper for bisecting Go compiler/runtime regressions that affect rclone. It is meant to run from the Go source tree, build the checked-out Go version, switch shell environment to a specific Go toolchain path, build rclone, and run a failing race test.

State and dependencies are deliberately user-local: it assumes Go source layout, `~/bin/use-go1.11`, a rclone checkout under `~/go/src/github.com/rclone/rclone`, `make`, and a local `race.go`. Exit `125` on Go build failure tells git-bisect to skip that revision. Risks are hard-coded personal paths and stale Go version naming; this is a template rather than general automation. Test signal is the bisect result itself.
