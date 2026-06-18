# sources/user-network-fs/rclone/bin/not-in-stable.go

Purpose: release helper that prints commits present on `master` but not on the previous minor stable branch. It reads `VERSION`, computes the previous stable prefix with semver, reads git logs from `<stable>.0..master` and `<stable>.0..<stable>-stable`, and compares commit subjects.

Important function: `readCommits` runs `git log --oneline`, parses hash/message with `logRe`, and returns both map and ordered list. State is read-only against git/VERSION; output is stdout. Dependencies are git and `coreos/go-semver`. Risks include matching by commit subject rather than patch identity, assuming branch names `master` and `vX.Y-stable`, and semver minor underflow if used near initial versions. Test signal is manual release review; no unit tests.
