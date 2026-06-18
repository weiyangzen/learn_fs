# sources/security-integrity/selinux/.github/actions/build-userspace/action.yml

Purpose: composite GitHub Action that builds and installs SELinux userspace for workflow matrix jobs.

Important inputs/outputs: inputs select Python, Ruby, compiler, and optional build variant. Output `DESTDIR` exposes `/tmp/destdir`. Steps set up Python and Ruby, install apt dependencies, optionally install clang, configure `CC`, `PYTHON`, `RUBY`, `DESTDIR`, and explicit make variable overrides.

Control flow: build step runs `make install` twice, then `make install-pywrap` and `make install-rubywrap`, with optional linker and debug/flag override variants.

State and dependencies: writes GitHub environment variables, uses apt, pip, bundler cache, and repository Makefiles.

Risks and test signals: duplicated `make install` may be intentional idempotence or accidental redundancy. Matrix variants exercise compiler, linker, flags, debug, and wrapper installation assumptions.
