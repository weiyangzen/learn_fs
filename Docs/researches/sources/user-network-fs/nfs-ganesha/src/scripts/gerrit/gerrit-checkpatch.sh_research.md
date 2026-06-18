# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-checkpatch.sh

## Purpose

`gerrit-checkpatch.sh` automates checkpatch review comments for Gerrit/GerritHub patchsets in the NFS-Ganesha project.

## Important APIs, Types, and Functions

Configuration variables define Gerrit server/user/key/project. `input_loop` streams or queries patchsets. `commit_review` submits JSON review output or prints it in dry-run mode. The main pipeline fetches refs, runs `git show --format=email`, pipes through `checkpatch.pl`, converts to JSON, and submits review.

## Control Flow

Options `-n`, `-q`, and `-c` select dry-run, one-shot query, or one-shot cat mode. Stream mode loops forever, reconnecting to `gerrit stream-events`. Each input line supplies `REF COMMIT`; the script fetches the ref and reviews the commit.

## State and Persistence Behavior

It mutates local git fetch state and remote Gerrit review comments. It stores no explicit local state; Gerrit comments are used to avoid duplicate query processing.

## Dependencies and Integration Points

It depends on ssh access to Gerrit, a `gerrit` git remote, `checkpatch.pl`, `gerrit-query.awk`, `gerrit-stream-filter.py`, and `checkpatch-to-gerrit-json.py`.

## Risks and Edge Cases

Hard-coded server/user/key/project limit portability. The loop can repeatedly reconnect and submit if filters fail. It assumes relative path `../checkpatch.pl` from the script directory/current working directory context. Python filter compatibility issues can break review submission.

## Test Signals

Dry-run tests with `-c` and known `REF COMMIT` input should validate generated JSON without remote submission. Query-mode tests can use captured Gerrit query output and AWK filter fixtures.
