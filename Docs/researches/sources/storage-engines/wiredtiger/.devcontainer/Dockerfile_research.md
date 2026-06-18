# sources/storage-engines/wiredtiger/.devcontainer/Dockerfile

## Purpose
This Dockerfile defines a VS Code devcontainer base image for WiredTiger development on Ubuntu 26.04. It installs compilers, CMake/Ninja, debugging tools, compression/security libraries, Python/SWIG tooling, and formatting/static-analysis utilities.

## Important APIs, Types, and Functions
The file uses Docker build instructions `FROM`, `RUN`, `USER`, `ENV`, and `WORKDIR`. It creates a non-root `wiredtiger` user and a Python virtual environment at `/home/wiredtiger/venv`.

## Control Flow, State, and Dependencies
Build flow updates apt metadata, installs packages without recommended extras, removes apt lists, creates the user, switches to that user, creates a venv, prepends it to `PATH`, and installs pinned Python packages (`find_libpython`, `gcovr`, `psutil`, `ruff`, `uv`). State is baked into the container image.

## Integration Points, Risks, and Test Signals
It supports the paired `devcontainer.json` and local CMake/Python/SWIG workflows. Risks include Ubuntu 26.04 package availability and pinned Python versions aging. Test signal is successful image build and ability to configure WiredTiger inside `/workdir`.
