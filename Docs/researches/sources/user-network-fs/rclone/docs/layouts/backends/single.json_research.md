<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/backends/single.json -->
# sources/user-network-fs/rclone/docs/layouts/backends/single.json

## Purpose

This Hugo template emits backend data as JSON for backend pages or data endpoints.

## Important APIs, Types, and Functions

It renders `hugo.Data.backends` through `jsonify` with two-space indentation.

## Control Flow

During a matching backend page render, Hugo evaluates the template and serializes all backend YAML data.

## State and Persistence Behavior

The template has no state. Output determinism depends on Hugo's data-map serialization order and the contents of `docs/data/backends`.

## Dependencies and Integration Points

It integrates with Hugo data loading and the backend YAML files in this subset.

## Risks and Test Signals

Risks include invalid JSON if template context changes or data contains unexpected values. Tests should build docs and parse the generated JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/backends/single.json -->
