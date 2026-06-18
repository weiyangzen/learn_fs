# sources/security-integrity/selinux/.github/workflows/run_tests.yml

Purpose: primary SELinux userspace GitHub Actions test workflow.

Important jobs/steps: triggers on push and pull_request, matrixes gcc/clang with multiple Python and Ruby versions plus build variants. It uses the local build action, downloads refpolicy headers, runs `make all`, sources `scripts/env_use_destdir`, runs `make test`, tests Python/Ruby imports except under sanitizers, runs flake8, and validates `.gitignore` plus `make clean distclean`.

Control flow: build, bootstrap refpolicy, build remaining targets, set test environment, run tests/wrappers/lint, then clean-state checks.

State and dependencies: uses `/tmp/destdir`, apt/pip/ruby setup, refpolicy network download, and many repository subdir Makefiles.

Risks and test signals: broad matrix catches compiler, linker, Python, Ruby, sanitizer, clean, and packaging regressions. External refpolicy availability is a CI risk.
