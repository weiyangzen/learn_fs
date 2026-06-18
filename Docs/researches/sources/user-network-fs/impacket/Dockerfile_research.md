# sources/user-network-fs/impacket/Dockerfile

## Purpose

The `Dockerfile` builds a small Alpine-based runtime image with Impacket installed into a Python virtual environment. It clones the upstream Fortra Impacket repository during image build rather than installing from the local build context.

## Important APIs, Types, and Functions

The first stage `compile` uses `python:3.13-alpine`, installs build dependencies (`git`, compiler toolchain, Python headers, libffi, OpenSSL, cargo), creates `/opt/venv`, clones `https://github.com/fortra/impacket.git` with depth 1, and installs `impacket/` with pip. The final stage also uses `python:3.13-alpine`, copies `/opt/venv`, sets `PATH`, and uses `/bin/sh` as entrypoint.

## Control Flow

Docker executes a multi-stage build: dependency-heavy compile stage first, then copies only the virtualenv into the final image. At container runtime, no Impacket command is executed by default; the user lands in a shell with Impacket console scripts available on `PATH`.

## State and Persistence Behavior

Build-time state includes a cloned upstream repository and virtualenv. Runtime persistent state is only container filesystem changes made by users. Because the build clones the remote repository, the image contents vary over time unless the upstream default branch is pinned externally.

## Dependencies and Integration Points

It depends on Docker, Alpine packages, PyPI, GitHub network access, and Impacket's install metadata. The CI workflow builds this image in the `docker` job. The image is intended for interactive Impacket use rather than repository-local development.

## Risks and Edge Cases

The build ignores the local source tree, so CI can pass Docker build even if local packaging is broken, and image contents may not match the commit being tested. Unpinned upstream clone and base image tags reduce reproducibility. Alpine/musl can expose dependency compatibility issues. Running as root and entering `/bin/sh` is convenient but not hardened.

## Test Signals

`docker build -t impacket:latests .` is the direct validation path in CI. A stronger test should run `docker run --rm impacket:latests python -c "import impacket"` and invoke a representative installed example command.
