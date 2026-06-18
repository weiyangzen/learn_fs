# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git_test.go

Purpose: integration tests for local repository creation and checkout behavior.

Important flow: tests skip unless hostname is `xfstests-kcs`; use `https://github.com/tytso/ext4.git`; create a repository id `test`; verify reference repo and working repo directories exist; delete and assert removal; checkout known tag/commit values.

State and dependencies: uses real `/cache/repositories`, network Git access, and KCS appliance host identity. It mutates cache state and may leave directories if interrupted.

Integration points: validates the same repository code KCS uses for builds and bisects.

Risks and test signals: not hermetic and only covers happy-path clone/delete/checkout. It does not cover bisect commands, BuildUpload, malformed URLs, concurrent access, or remote watcher updates.
