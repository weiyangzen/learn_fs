<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/Dockerfile -->
# sources/object-store/minio-mc/Dockerfile

## Purpose
Multi-stage Dockerfile building and packaging the latest `mc` binary into a scratch image.

## Important APIs, types, and functions
Build stage uses `golang:1.22-alpine`, installs CA certificates and curl, fetches LICENSE/CREDITS, and runs `go install` with ldflags from `buildscripts/gen-ldflags.go`. Final stage copies `mc`, licenses, and CA bundle into scratch and sets entrypoint.

## Control flow
Docker builds the Go binary in Alpine, then copies only the executable and support files into a minimal runtime image.

## State and persistence behavior
No app persistence. The image contains a static binary and CA store.

## Dependencies and integration points
Depends on network access to GitHub/raw license files and Go module install of `github.com/minio/mc@latest`.

## Risks and test signals
Using `@latest` means builds are not tied to the local checkout. Test signal is successful `docker build` and `mc --help` in the image.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/Dockerfile -->
