# sources/user-network-fs/impacket/.github/labeler.yml

## Purpose

`.github/labeler.yml` defines pull request label rules for the Impacket repository. It maps changed file path patterns to labels such as Examples, Library, CI/CD & Tests, Setup, and Docs.

## Important APIs, Types, and Functions

This is declarative YAML for `srvaroa/labeler`. Top-level `version: 1` selects the labeler config format. Each `labels` entry contains a `label` string and `files` regex-style path patterns.

## Control Flow

Runtime control flow is owned by the labeler GitHub Action. On pull request events, `.github/workflows/labeler.yml` invokes the action, which reads this file, matches changed paths against configured patterns, and applies corresponding labels.

## State and Persistence Behavior

The file itself is repository configuration. Persistent state effects occur in GitHub pull request metadata when labels are applied. No local build or runtime state is changed.

## Dependencies and Integration Points

It integrates with `.github/workflows/labeler.yml` and the `srvaroa/labeler@master` action. Labels align with major repository areas: `examples/`, `impacket/`, `tests/`, workflow/config files, setup files, and docs/license files.

## Risks and Edge Cases

Pattern semantics depend on the external labeler action. Broad patterns such as `.github/.*` and `*.md` may over-label repository-root changes, while nested markdown files may or may not match depending on the action's regex handling. Using label names that do not exist may require the action to create them or fail depending on repository permissions.

## Test Signals

Validation is best done by opening test pull requests or running the labeler action in CI against synthetic changed-file lists. A workflow run with expected labels on examples, library, CI, setup, and docs changes is the primary signal.
