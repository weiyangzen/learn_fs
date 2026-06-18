<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/mkdocker.sh -->
# sources/security-integrity/libcap/contrib/bug216610/mkdocker.sh

## Purpose
Generates a Dockerfile for bug216610 cross-compilation with host-specific builder UID/GID.

## Important APIs, Types, And Functions
Shell here-document emits Debian base image, cross-compiler installs, `/shared` directory, and passwd/shadow entries using `id -u` and `id -g`.

## Control Flow
Runs once and writes Dockerfile text to stdout.

## State And Persistence Behavior
Does not mutate files by itself; callers redirect output to `Dockerfile`.

## Dependencies And Integration Points
Used by the bug216610 makefile `Dockerfile` target.

## Risks And Edge Cases
Generated image is based on floating `debian:latest`. `chown builder.bin` assumes a `bin` group exists in the base image.

## Test Signals
Signals are a usable Dockerfile and matching host UID/GID for mounted build outputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/mkdocker.sh -->
