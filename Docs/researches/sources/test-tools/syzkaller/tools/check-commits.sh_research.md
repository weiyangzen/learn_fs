## sources/test-tools/syzkaller/tools/check-commits.sh

This CI/local helper validates commit subject format and body line length. It determines the commit range from `GITHUB_PR_HEAD_SHA` and `GITHUB_PR_COMMITS`, or falls back to `master..HEAD`, or one commit if no range is found. It checks each commit subject against syzkaller's `subsystem/path: lowercase description without trailing period` style or revert format, and rejects non-dependabot commit bodies with lines over 120 characters.

State is read from git history and environment variables; output uses GitHub Actions `##[error]` annotations. Dependencies are bash, git, regex matching, and `wc`. Risks include backtick command substitution style, assumptions about `master`, subject regex strictness, and body long-line regex behavior. There are no direct tests.
