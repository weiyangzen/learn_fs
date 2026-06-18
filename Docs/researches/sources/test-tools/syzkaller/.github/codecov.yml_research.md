<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/codecov.yml -->
# sources/test-tools/syzkaller/.github/codecov.yml research

Purpose: Codecov configuration for syzkaller coverage uploads.

Important APIs, types, and functions: it disables `require_ci_to_pass`, sets coverage display precision/range, makes project and patch statuses informational with threshold 100 percent and target 0 percent, configures comments after two builds, disables GitHub check annotations, and rewrites checkout paths with `fixes`.

Control flow: Codecov reads this file during upload, normalizes paths from the GitHub Actions GOPATH checkout, and posts informational coverage results and file-oriented comments.

State and persistence: the file stores reporting policy only. Coverage data is uploaded by CI artifacts and Codecov's service.

Dependencies and integration: used by `.github/workflows/upload-coverage.yml`, which points the Codecov action at the trusted base-repository copy.

Risks: informational statuses avoid blocking PRs even on large coverage regressions. The broad 100 percent threshold and 0 percent target make the status intentionally non-gating. Path fixes must match the CI checkout path.

Test signals: Codecov validation, successful unittests/dashboard flag uploads, correctly normalized file paths, and a comment appearing after both expected coverage artifacts are processed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/codecov.yml -->
