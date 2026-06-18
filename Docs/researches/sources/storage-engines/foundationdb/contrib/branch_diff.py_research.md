# sources/storage-engines/foundationdb/contrib/branch_diff.py

## Purpose
Command-line helper that compares two git branches and emits a Markdown table of merged GitHub pull requests associated with non-merge commits present in `TO` but not `FROM`.

## Important APIs, Types, And Functions
`parse_args()` defines `--from`, `--to`, and optional `--output`. `diff_branches_by_commit()` runs `git log FROM..TO --no-merges --oneline` and returns short commit hashes. `PullRequestInfo` stores PR number, author, title, and associated commits. `get_pr_from_commit()` calls GitHub CLI `gh pr list` against `apple/foundationdb`. `render_markdown_table()` writes the final `PR ID`, `Author`, `Title` table.

## Control Flow
`main()` parses arguments, gathers diff commits, queries GitHub for each commit, deduplicates by PR number, prints progress, and renders to stdout or an output file. Missing PRs are logged to stderr and skipped.

## State And Persistence
No persistent state except the optional output Markdown file. It relies on local git repository state and GitHub CLI auth/session state.

## Dependencies And Integration
Requires `git`, `gh`, network access, and JSON output from GitHub CLI. It is a release/maintenance utility independent from FoundationDB server code.

## Risks
`line[:9]` on split output can produce an empty hash for a trailing newline. The first GitHub search result is trusted even if multiple PRs match. Author name may be absent or empty. Output files are opened without context management. Broad `except:` hides malformed response details. Markdown table cells are not escaped.

## Test Signals
Mock `subprocess.run` for git and gh failure/success paths; test empty diffs, duplicate PRs, output rendering with pipes in titles, and missing author fields.
