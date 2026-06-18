# sources/security-integrity/fsverity-utils/scripts/run-tests.sh

Purpose: This shell script runs the fsverity-utils test suite, including library unit tests, CLI command checks, and optional kernel/filesystem integration tests.

Important APIs and steps: It builds or invokes test binaries, creates temporary files, computes/signs/enables/verifies digests, checks command output, and skips or adapts when kernel fs-verity support is unavailable.

Control flow and state: The script creates temporary directories and files, runs commands with expected statuses, and cleans up. Successful ioctl tests persist fs-verity metadata on temporary files only.

Dependencies and integration points: Integrates `fsverity` CLI, library test binaries, OpenSSL fixtures, Linux fs-verity support, and CI.

Risks and test signals: Integration tests are environment-sensitive due to filesystem/kernel requirements. Signals include deterministic digest vectors, signing tests, command usage checks, and clear skips when prerequisites are missing.
