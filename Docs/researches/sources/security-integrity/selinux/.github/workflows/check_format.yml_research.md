# sources/security-integrity/selinux/.github/workflows/check_format.yml

Purpose: GitHub Actions workflow enforcing C/H formatting.

Important jobs/steps: triggers on push and pull_request to `main`, runs in `fedora:latest`, checks out code, installs `make` and `clang-tools-extra`, and runs `make check-format`.

Control flow: simple single-job format gate. The top-level Makefile selects all C/H files under `SUBDIRS` and invokes `clang-format --dry-run -Werror`.

State and dependencies: depends on Fedora package names and repository Makefile format target. No persistent state beyond CI workspace.

Risks and test signals: branch trigger uses `main`, while other workflows use `master`; that mismatch may affect coverage depending on repository default branch. Signal is purely style conformance.
