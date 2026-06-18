# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-stream-filter.py

## Purpose

`gerrit-stream-filter.py` filters Gerrit stream-events JSON and emits patchset refs/revisions for patchset-created events in the target project.

## Important APIs, Types, and Functions

Top-level code reads optional project name from argv, parses JSON lines from stdin, filters by `type == patchset-created` and `change.project`, and prints `patchSet.ref patchSet.revision`.

## Control Flow

Malformed JSON lines are skipped. Matching events are optionally debug-printed, then emitted and stdout is flushed for pipeline responsiveness.

## State and Persistence Behavior

No persistent state exists.

## Dependencies and Integration Points

It depends on Python `json` and `sys`. `gerrit-checkpatch.sh` consumes its output in stream mode.

## Risks and Edge Cases

The script assumes all parsed JSON objects have `type`, `change`, and `patchSet` keys; unrelated Gerrit events missing those keys can raise `KeyError`. The shebang is generic `python`, though the code is mostly Python 2/3 compatible due to `unicode` literals only.

## Test Signals

Feed fixtures for matching events, other projects, other event types, malformed JSON, and events missing optional fields. Verify line-buffered output in pipeline mode.
