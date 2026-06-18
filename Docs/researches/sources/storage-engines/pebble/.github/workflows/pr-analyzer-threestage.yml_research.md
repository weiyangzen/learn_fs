# sources/storage-engines/pebble/.github/workflows/pr-analyzer-threestage.yml

## Purpose
This workflow runs a staged Claude Code review on pull requests, escalating from initial bug screening to database-expert review to principal-engineer review before commenting on the PR.

## Important APIs, types, and functions
It triggers on `pull_request_target` synchronize/ready/reopened events unless label `O-No-AI-Review` is present. It uses `actions/checkout@v5`, Google workload identity authentication, `cockroachdb/claude-code-action@v1`, `jq` extraction from execution files, `gh pr comment`, and PR label editing.

## Control flow
The job checks out the PR head SHA, authenticates to Vertex-backed Claude, and runs Stage 1. If Stage 1 output contains potential bug text, Stage 2 runs; if Stage 2 confirms, Stage 3 runs. Each result is extracted from the action execution file into step outputs. A final analysis report always runs. If Stage 3 confirms a potential bug, the workflow posts a PR comment with review instructions and adds a label.

## State and persistence behavior
The workflow can write PR comments and labels. It reads PR code under `pull_request_target`, but tool permissions are restricted mostly to read/diff commands and PR metadata.

## Dependencies and integration points
It integrates GitHub PR events, Google Cloud workload identity, Anthropic Vertex model routing, and CockroachDB's Claude action. The workflow depends on exact marker strings in model outputs for control flow.

## Risks and edge cases
`pull_request_target` with PR head checkout is sensitive; allowed tools must remain restricted because untrusted code is present. String matching on model output is brittle. The prompt contains unusually forceful language that may bias output. Model/version or action changes can break JSON extraction or result formats.

## Test signals
Dry runs should validate skipped behavior with `O-No-AI-Review`, Stage 1 no-bug path, staged escalation path, result extraction from execution files, final report generation, PR comment creation, and label application.
