# sources/user-network-fs/pyfuse3/pyproject.toml

Purpose: Defines pyfuse3 packaging, build backend, runtime and development dependencies, package discovery, included package data, and static-analysis configuration.

Important APIs/types/functions: The `[build-system]` uses `setuptools>=78.1.1`, `setuptools_scm>=8.0`, `Cython`, and custom backend `build_backend` from `util`. `[project]` declares the distribution metadata and dynamic version. `[dependency-groups].dev` lists pyright, mypy, pytest, pytest-trio, ruff, sphinx, and twine. Tool sections configure setuptools, ruff/isort, mypy, pyright, codespell, and ruff formatting.

Control flow: Build frontends load `util/build_backend.py` through `backend-path`. Setuptools discovers packages under `src` and includes `pyfuse3/py.typed`. Versioning is delegated to setuptools-scm.

State and persistence: No runtime state; the file persists build and lint policy. It affects generated wheels/sdists and type-check/lint behavior across the project.

Dependencies and integration points: Integrates with the Python packaging ecosystem, Cython extension build, setuptools-scm, and type/lint tools. Runtime requires Python `>=3.10` and `trio >= 0.15`.

Risks: Build success depends on custom backend logic and system `pkg-config`/libfuse availability outside this file. Mypy and pyright exclude `util/` and `rst/conf.py`, so those files rely on runtime/testing more than type checks.

Test signals: Indirectly exercised by package builds, editable installs, and CI lint/type jobs. The configured dev dependencies are the tools expected for local validation.
