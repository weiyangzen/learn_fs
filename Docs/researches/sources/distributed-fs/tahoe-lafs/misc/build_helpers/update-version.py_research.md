# sources/distributed-fs/tahoe-lafs/misc/build_helpers/update-version.py

## Purpose

This release helper computes the next Tahoe-LAFS release version from existing Git tags and optionally creates an annotated signed tag.

## Important APIs, Types, and Functions

`existing_tags(git)` reads Dulwich tags beginning with `tahoe-lafs-` and parses them as `packaging.version.Version`. `create_new_version(git)` increments the highest tag's minor version and resets patch to zero. `main(reactor)` checks repository cleanliness, handles `--no-tag`, computes a UTC-day-quantized tag timestamp, and calls `dulwich.porcelain.tag_create`.

## Control Flow

The script runs under Twisted `react`. It aborts on staged or unstaged changes. With `--no-tag`, it prints the computed version only. Otherwise it prints existing tags, creates `tahoe-lafs-X.Y.0` on `HEAD`, and prints a push hint.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is a new local Git tag. Dependencies are Dulwich, Twisted, and `packaging`. Integration is manual release workflow. Risks include failure when no matching tags exist, minor-only version policy, hard-coded signing identity, local-time `datetime.now()` mixed with UTC tuple conversion, and a push hint missing the `tahoe-lafs-` prefix. Tests should use temporary Dulwich repos for clean/dirty states, tag parsing, `--no-tag`, and timestamp/signing arguments.
