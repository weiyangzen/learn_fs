# sources/sync-backup/borg/src/borg/upgrade.py

## Purpose
Defines `UpgraderNoOp`, the baseline upgrader used when no transformation is required during archive/item/chunk transfer. It preserves selected archive metadata while dropping version/stats-specific fields.

## Important APIs, Types, and Functions
Class `UpgraderNoOp` exposes `new_archive`, `upgrade_item`, `upgrade_compressed_chunk`, and `upgrade_archive_metadata`. It stores `args` from initialization and inspects `args.chunker_params`.

## Control Flow
Most hooks are identity/no-op paths: new archives do nothing, items are returned unchanged, and compressed chunks return their metadata/data pair. Archive metadata is copied into a new dictionary for allowed attributes, with `cwd` normalized through `getattr`.

## State and Persistence Behavior
No file-backed state is owned. The returned metadata dictionary controls what future archive metadata persistence will include. Rechunking replaces `chunker_params` with CLI-provided values.

## Dependencies and Integration Points
Integrates transfer/upgrade code with archive save logic that interprets `cwd=None` as "leave unset". Uses Borg logger creation but does not log in this implementation.

## Risks and Test Signals
Risks are dropping metadata that should survive upgrade, retaining stale version/stats fields, or mishandling rechunking parameters. Tests should assert preserved fields, intentional omission of stats/version, identity item/chunk paths, and chunker replacement when requested.
