# sources/sync-backup/borg/scripts/msys2-install-deps

Purpose: Installs Borg build/runtime dependencies in an MSYS2 UCRT64 environment using `pacman`.

Important APIs/types/functions: Invokes `pacman -S --needed --noconfirm` with Git, UCRT64 toolchain/pkgconf/lz4/openssl/rclone, Python, Cython, setuptools/wheel/build/pkgconfig/packaging/pip/paramiko, Rust, maturin, msgpack, argon2-cffi, and platformdirs packages. If first argument is `development`, installs pytest, pytest-benchmark, pytest-cov, and pytest-xdist packages.

Control flow: Runs base install unconditionally, then conditionally installs development test packages when `$1 = development`.

State and persistence: Mutates the MSYS2 package database and installed package set.

Dependencies and integration points: Requires Bash and `pacman` in an MSYS2 UCRT64 environment. Supports Windows/MSYS2 Borg development and packaging.

Risks: Accessing `$1` under no arguments is safe here because `set -u` is not enabled, but it is still loose. No error handling beyond pacman exit status. Package names can drift as MSYS2 updates.

Test signals: Run in a clean MSYS2 UCRT64 image with and without `development`, then run `python -m build`, selected pytest/tox commands, and import checks for compiled/native dependencies.
