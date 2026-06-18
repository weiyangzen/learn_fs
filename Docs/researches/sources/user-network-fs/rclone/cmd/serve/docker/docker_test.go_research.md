# sources/user-network-fs/rclone/cmd/serve/docker/docker_test.go

## Purpose

This test file validates Docker plugin driver logic and, when possible, end-to-end Docker plugin API serving.

## Important APIs, Types, and Functions

Helpers include `initialise`, `assertErrorContains`, `assertVolumeInfo`, `APIClient`, `newAPIClient`, `APIClient.request`, and `testMountAPI`. Tests include `TestDockerPluginLogic`, `TestDockerPluginMountTCP`, and `TestDockerPluginMountUnix`.

## Control Flow

`TestDockerPluginLogic` uses a dummy driver to create volumes, validate bad options, list/get, mount with multiple IDs, restore saved state, and remove after unmount. API tests start a real server, call Docker endpoints, write through the mounted path, then unmount and remove.

## State and Persistence Behavior

Tests redirect rclone cache dir to a temp directory so `docker-plugin.state` is isolated. Dummy tests exercise persistence without real mounts.

## Dependencies and Integration Points

They depend on local and memory backends, mount/cmount packages, mountlib availability, Docker API JSON, TCP/Unix sockets, and filesystem cleanup helpers.

## Risks and Test Signals

The file has `!race` and skips or marks real mount tests unreliable on some platforms, so concurrency and real mount coverage may be absent in CI. The tests still provide strong signals for state restoration, request reference counting, and API error formatting.
