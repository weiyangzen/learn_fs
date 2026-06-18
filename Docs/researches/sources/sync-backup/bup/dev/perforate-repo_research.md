# sources/sync-backup/bup/dev/perforate-repo

## Purpose
Developer tool to intentionally remove selected object IDs from a Git/bup repository and repack it, creating damaged repositories for recovery/check tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-python`, uses `argparse`, `git cat-file --batch-all-objects`, `git unpack-objects`, `git pack-objects`, `TemporaryDirectory`, and `unlink`.

## Control Flow
Requires `--drop-oids` and a repository. It unpacks all packs into a temporary bup repo, verifies object sets match, reads 40-character OIDs from stdin, deletes corresponding loose objects, removes original pack-related files, and repacks remaining objects into the original pack directory.

## State and Persistence Behavior
Destructively rewrites repository pack state and deletes selected objects. Temporary repo is under the victim repo and removed after use.

## Dependencies and Integration Points
Integrates Git plumbing with bup repository layout; caller must reset midx/bloom if needed.

## Risks and Test Signals
High risk by design: data loss, assumptions about no loose objects, SHA1-only OID regex, and locale/path assumptions. Signals are object-set verification and successful repack.
