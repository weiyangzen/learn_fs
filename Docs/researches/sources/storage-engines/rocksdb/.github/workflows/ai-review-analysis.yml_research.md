<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-analysis.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/ai-review-analysis.yml

Purpose: Reusable workflow implementing shared Claude/Codex PR analysis for automatic and manual AI review/query requests.

Important APIs/types/functions: `workflow_call` inputs select provider, display name, slash commands, artifact/comment filenames, default/selected/classifier/recovery models, thinking budget, dispatch PR number, and authorized users. Jobs are `auto-review` and `manual-review`. Major steps gather PR info, gate early reviews, avoid duplicate review artifacts, checkout base repo, install Codex, generate prompts/diffs, classify complexity, run Claude or Codex, recover partial findings, build comments through parser scripts, and upload artifacts/logs.

Control flow: auto mode runs on `pull_request_target` for same-repo PRs after a checks threshold or on `workflow_run` fallback after PR CI success. It skips stale SHAs and existing comments. Manual mode accepts `workflow_dispatch` or authorized issue comments containing review/query commands, resolves PR metadata, builds either review or query prompts, and runs the chosen provider with optional model/budget overrides.

State and persistence behavior: writes temporary diff/prompt files, review outputs, execution logs, metadata files (`pr_number.txt`, `trigger_type.txt`, `head_sha.txt`, etc.), and uploads short-retention artifacts consumed by the comment workflow. It does not post comments directly.

Dependencies and integration points: called by `claude-review.yml` and `codex-review.yml`; depends on GitHub REST via `actions/github-script`, `actions/checkout`, `actions/setup-node`, `@openai/codex`, `anthropics/claude-code-base-action`, parser scripts, prompt files under `claude_md`, and repository PR CI workflow names.

Risks: Codex runs with `--dangerously-bypass-approvals-and-sandbox`; the workflow limits that to read-only analysis and same-repo early triggers, but it is still arbitrary command execution on the runner. Diff truncation can miss issues. Early-review gate can skip reviews due to CI timing. Secrets must be present for provider execution. Manual authorization is a hardcoded JSON list.

Test signals: uploaded provider result artifact, execution log artifacts, skip reasons in logs, generated comment markdown, and successful downstream comment workflow posting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-analysis.yml -->
