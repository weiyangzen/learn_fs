## sources/user-network-fs/pyfuse3/.github/workflows/test.yml

Purpose: GitHub Actions CI workflow for pyfuse3 build, lint, type checking, tests, and docs.

Important APIs/types/functions: Matrix covers Python 3.10 through 3.14 on Ubuntu 24.04, installs uv, Linux FUSE/build dependencies, runs `uv sync --locked`, ruff check/format diff, mypy, pyright, pytest, and sphinx with warnings as errors.

Control flow: Triggered on push; fail-fast matrix stops after first failed lane.

State and persistence: Uses uv cache from setup action and CI artifacts/logs only.

Dependencies and integration: Requires libattr, libfuse3, fuse3, pkg-config, gcc, uv, and the repository lockfile.

Risks and test signals: FUSE tests may require CI kernel/user permissions, Python 3.14 compatibility is an active signal, and docs warnings fail builds. Local reproduction should use the same uv commands and apt packages.
