# sources/user-network-fs/rclone/cmd/selfupdate/noselfupdate.go

Purpose: build-tag alternative for `noselfupdate` builds.

Important behavior: init appends `"noselfupdate"` to `buildinfo.Tags`, exposing the build capability state in version/build metadata.

Control flow/state: no runtime command behavior and no persistence beyond mutating process build-info metadata at startup.

Dependencies/integration: `lib/buildinfo`. Risks are build-tag drift with docs/tests that assume `selfupdate` exists or that version output includes the tag. Coverage is build-matrix dependent.
