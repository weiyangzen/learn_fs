<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/checkdeps.sh -->
# sources/object-store/minio-mc/buildscripts/checkdeps.sh

## Purpose
Build dependency and platform guard script used before compiling MinIO client.

## Important APIs, types, and functions
Sources `buildscripts/build.env`, defines `_init`, custom portable `readlink`, `assert_is_supported_arch`, `assert_is_supported_os`, `assert_check_golang_env`, `assert_check_deps`, and `main`.

## Control flow
Initializes minimum versions and host OS/arch, then checks architecture, OS, Go presence/minimum version, and Git minimum version. Errors print explanatory messages and exit nonzero.

## State and persistence behavior
No persistent state; only process environment and shell options are touched.

## Dependencies and integration points
Called by Makefile `checks` and `build`. Depends on shell utilities, Go, Git, Perl, sed, and `check_minimum_version` from sourced build env.

## Risks and test signals
Minimum `GO_VERSION=1.13` is much older than CI's Go 1.25, so it may not reflect real module requirements. Signals are successful `make checks` on supported platforms and clear failures on unsupported hosts.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/checkdeps.sh -->
