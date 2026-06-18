<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Dockerfile -->
# sources/security-integrity/libcap/contrib/bug216610/Dockerfile

## Purpose
Docker build environment for bug216610 cross-compilation experiments.

## Important APIs, Types, And Functions
Uses Debian latest, installs ARM and AArch64 cross GCC/binutils packages, creates `/shared`, and adds a `builder` user.

## Control Flow
Docker build runs package update/install steps and creates user/home metadata.

## State And Persistence Behavior
Persists compiler packages and user entries inside the image. Host source is mounted at runtime by the makefile.

## Dependencies And Integration Points
Used by `bug216610/Makefile` `arms` target with `docker run -v $PWD/c:/shared`.

## Risks And Edge Cases
`debian:latest` is not pinned, so package versions can drift. The checked-in Dockerfile has fixed UID/GID 1000 while `mkdocker.sh` can generate host-specific IDs.

## Test Signals
Signals are successful image build and cross-compiled `.syso` files.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Dockerfile -->
