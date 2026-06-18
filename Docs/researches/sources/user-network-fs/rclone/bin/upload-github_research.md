# sources/user-network-fs/rclone/bin/upload-github

Purpose: publishes an rclone GitHub release using the `gh` CLI. It creates temporary release notes linking to the latest changelog anchor, creates a draft release, uploads build artifacts, marks the release non-draft, views it, and prints done.

State changes are remote GitHub release creation and artifact uploads; local state includes a temp release-notes file. Dependencies are `gh`, authenticated permissions on `rclone/rclone`, populated `build/`, and changelog heading format. Risks include uploading unintended build files except explicit `current`/`testbuilds` skips, clobbering assets, immediately publishing after upload, and anchor derivation mismatch. Test signal is `gh release view` success.
