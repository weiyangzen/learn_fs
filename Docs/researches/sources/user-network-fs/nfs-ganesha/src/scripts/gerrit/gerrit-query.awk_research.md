# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-query.awk

## Purpose

`gerrit-query.awk` filters `gerrit query --comments --patch-sets` output to find open patchsets that do not already have a review by the trigger user.

## Important APIs, Types, and Functions

The AWK script tracks `patchSets[curSet]["reviewed"]`, `ref`, and `commit`; `username`; and current patchset number. It prints `ref commit` for unreviewed patchsets when a new `change` starts.

## Control Flow

On `change` lines it flushes accumulated patchsets, printing those without a `reviewed` marker, then resets state. It detects trigger comments when `username` is `ganesha-triggers` and message starts `Patch Set`, records patchset refs/revisions from query output, and supports optional `debug`.

## State and Persistence Behavior

State is in-memory per input stream. There is no persistence.

## Dependencies and Integration Points

It depends on AWK, with comments noting AWK >= 4 for one-shot query use. `gerrit-checkpatch.sh` invokes it.

## Risks and Edge Cases

The script flushes when the next `change` begins, so the last change may not be emitted unless the input format includes a trailing change or EOF handling is added. Parsing is tightly coupled to Gerrit text output formatting.

## Test Signals

Fixture tests with one/multiple changes, reviewed/unreviewed patchsets, and EOF-only final changes should verify emitted refs. Run with the target AWK implementation.
