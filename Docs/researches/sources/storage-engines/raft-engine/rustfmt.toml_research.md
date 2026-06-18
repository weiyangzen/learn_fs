# sources/storage-engines/raft-engine/rustfmt.toml

## Purpose
Configures rustfmt behavior for the raft-engine workspace.

## Important APIs, Types, And Functions
The only setting is `wrap_comments = true`, enabling comment wrapping during formatting.

## Control Flow
`cargo fmt --all`, invoked by the Makefile and developers, reads this file and applies the setting to Rust source formatting.

## State And Persistence Behavior
It affects source formatting only and has no runtime or persistence impact.

## Dependencies And Integration Points
Integrates with rustfmt installed by CI, the `make format` target, and the stable toolchain component list in the GitHub workflow.

## Risks And Edge Cases
Comment wrapping can create larger diffs when comments are reformatted, especially around long URLs, generated comments, or carefully aligned documentation.

## Test Signals
The main signal is `cargo fmt --all --check` or `make format` producing no unexpected diff.
