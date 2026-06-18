# sources/test-tools/stress-ng/.github/workflows/ci-builds.yml

Purpose: manually triggered GitHub Actions build matrix for stress-ng across Ubuntu GCC, Ubuntu clang/static analyzer, Ubuntu arm64, FreeBSD cross-build, macOS universal flags, and Cygwin.

Important APIs and control flow: `workflow_dispatch` inputs select platform substrings, optional package lists, make options, and quick-check options. Each job gates with `contains(github.event.inputs.platforms, ...)`, installs dependencies, checks out source, builds with `make`, runs `./stress-ng --version`, runs a short stress-ng check where native execution is possible, and uploads artifacts.

State and persistence: persists artifacts for 30 days; otherwise state is CI workspace-only.

Dependencies and integration: uses `actions/checkout@v4`, `actions/upload-artifact@v4`, `scan-build`, a smartmontools FreeBSD cross container, macOS toolchains, and `cygwin/cygwin-install-action`.

Risks and test signals: substring gating can unintentionally select platforms if names overlap; optional package input is shell-interpolated; Cygwin safe-directory handling is brittle. Signals are successful builds, analyzer report artifact, binary artifact upload, and quick check output.
