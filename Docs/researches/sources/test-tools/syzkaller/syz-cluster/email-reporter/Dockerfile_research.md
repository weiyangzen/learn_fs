# sources/test-tools/syzkaller/syz-cluster/email-reporter/Dockerfile

## Purpose
Builds the email-reporter runtime container from a prebuilt syz-cluster builder image.

## Important APIs, types, and functions
Uses Dockerfile syntax 1.7 labs. Build args `IMAGE_PREFIX` and `IMAGE_TAG` select `${IMAGE_PREFIX}syz-cluster-build:${IMAGE_TAG}` as the builder. Runtime image is `alpine:latest`, installs `git`, copies `/build/syz-cluster/bin/email-reporter` to `/bin/email-reporter`, and sets that binary as entrypoint.

## Control flow
The binary is expected to be produced in the builder image. At runtime the container starts the email reporter directly. `git` is installed because Lore polling clones/fetches an archive repository.

## State and persistence behavior
The container itself is stateless; persistent Lore checkout state is mounted by Kubernetes at `/lore-repo`.

## Dependencies and integration points
Integrates with the build system's `syz-cluster-build` image, `email-reporter/deployment.yaml`, and `MakeLorePoller`, which uses `/lore-repo/checkout`.

## Risks and edge cases
`alpine:latest` is floating, so rebuilds may change runtime contents. The image relies on the builder path and binary name remaining stable. Missing `git` would break Lore polling.

## Test signals
Container behavior is indirectly covered by local cluster smoke tests and Go tests for the binary logic, but this Dockerfile has no direct build test in the assigned files.
