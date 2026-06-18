# sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage_test.go

## Purpose
This file runs the GCS backend through rclone's generic integration tests with and without directory markers.

## Important APIs, Types, And Control Flow
`TestIntegration` runs against `TestGoogleCloudStorage:`. `TestIntegration2` skips when an explicit `-remote` is set, then runs the same backend with extra config enabling `directory_markers`.

## State And Persistence
The tests create and delete buckets/objects through the configured GCS remote. The second test persists empty directory behavior remotely through marker objects during the run.

## Dependencies And Integration Points
It depends on the production `googlecloudstorage` package, `fstest`, and `fstests`. Extra config is passed through `fstests.ExtraConfigItem`.

## Risks And Test Signals
The tests verify broad fs behavior and specifically ensure the directory-marker feature remains compatible with the generic suite. They require live GCS credentials and project/bucket permissions.
