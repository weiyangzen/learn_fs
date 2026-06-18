# sources/sync-backup/borg/pyproject.toml

Purpose: Central Python project metadata and tool configuration for BorgBackup. It defines packaging metadata, runtime/optional/build dependencies, console entry points, setuptools discovery, lint/type/test configuration, tox environments, Bandit, and coverage behavior.

Important APIs/types/functions: Exposes project scripts `borg = borg.archiver:main` and `borgfs = borg.archiver:main`. Runtime dependencies include `borghash`, `borgstore[rest]`, `msgpack`, `packaging`, platform-specific `platformdirs`, `argon2-cffi`, `shtab`, `backports-zstd` for Python <3.14, `jsonargparse`, `PyYAML`, and `blake3`. Optional extras select FUSE (`llfuse`, `pyfuse3`, `mfusepy`), store backends (`s3`, `sftp`, `rclone`), `nofuse`, and `cockpit`.

Control flow: Build frontends use `setuptools.build_meta` with build requirements including Cython and `setuptools_scm`, writing `src/borg/_version.py`. Tox expands env lists across Python 3.11-3.15 and FUSE implementations, with dedicated docs, ruff, mypy, bandit, and sha256-pack-id environments.

State and persistence: Packaging creates installed metadata, generated `_version.py`, wheels/sdists, coverage XML, JUnit XML, and test build artifacts. Tool sections persist policy for format/lint/type/test runs.

Dependencies and integration points: Integrates with `scripts/make.py`, Cython extension build, docs generation, tox CI, pytest, ruff, mypy, Bandit, coverage, and optional backend/FUSE tests. `include-package-data` and `exclude-package-data` keep generated C/Pyrex sources out of packages.

Risks: Python version/dependency pin drift can break builds. The broad `pass_env = ["*"]` makes tox sensitive to caller environment. Optional FUSE/backend extras influence test matrix and runtime feature availability.

Test signals: `tox -e ruff,mypy,docs,bandit` and Python/FUSE tox envs are the declared validation gates. Packaging should be tested with `python -m build`; console script import should be validated from installed wheels.
