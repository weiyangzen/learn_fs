<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/.github/workflows/differential-shellcheck.yml -->
# sources/test-tools/strace/.github/workflows/differential-shellcheck.yml

Purpose: GitHub Actions workflow that runs ShellCheck only on changed shell code and uploads SARIF output.

Important jobs: single `lint` job on `ubuntu-latest`, using pinned `actions/checkout`, pinned `redhat-plumbers-in-action/differential-shellcheck`, and pinned `actions/upload-artifact`. Permissions are minimal at workflow level and grant `security-events: write` for SARIF handling.

Control flow: runs on pushes and pull requests targeting `master`. Concurrency cancels older runs for the same PR/ref. The check receives `severity: warning` and the GitHub token, then artifact upload runs under `always()`.

State and persistence: stores a SARIF artifact named `Differential ShellCheck SARIF`; no repo files are modified.

Dependencies and integration: complements CI shell scripts and uses Git history (`fetch-depth: 0`) to compute differentials.

Risks: differential linting can miss pre-existing issues outside touched lines. Upload may run even if the check step produces no SARIF path, depending on action behavior. Test signals: PR checks should annotate changed shell issues and always provide a SARIF artifact when the action emits one.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/.github/workflows/differential-shellcheck.yml -->
