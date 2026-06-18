# File Research: sources/local-fs/xfsdump/common/drive.c

Purpose: generic drive-selection and drive-manager initialization layer.

Key behavior:
- Declares available strategies: simple, SCSI tape, and remote tape (`drive_strategy_rmt`).
- `drive_init1` parses dump/restore destination/source options, allocates `drive_t` descriptors, computes `partialmax`, handles stdin/stdout style `-`, and selects the best strategy by score.
- Strategy precedence array is simple, SCSI tape, then remote tape; highest score wins.
- Selected strategy fills `d_strategyp`, recommended mark separation/file size, and runs `ds_instantiate`.
- `drive_init2` allocates per-drive read/write headers and calls each drive’s `do_init`.
- `drive_init3` calls each drive’s `do_sync`.
- `drive_mark_commit` invokes callbacks for queued marks with offsets up to the committed byte count.
- `drive_mark_discard` invokes callbacks for all remaining marks with `committed = FALSE`.
- `drive_display_metrics` calls each strategy’s metrics callback when provided.

Important details:
- `drive_alloc` canonicalizes paths relative to `homedir`, except reserved `"stdio"`, and detects named/unnamed pipes.
- `drive_allochdrs` embeds `drive_hdr_t` pointers into `global_hdr_t.gh_upper`; dump write headers are copied from a global template and populated with drive strategy id, drive index, and drive count.
- `partialmax` is `(drivecnt * 2) - 1` for multi-drive restore/dump, else zero.

Interactions:
- Implements globals declared in `drive.h`: `drivepp`, `drivecnt`, `partialmax`.
- Consumed by dump/restore main/content layers to obtain configured `drive_t` managers.
- Depends on `path_reltoabs`, `dlog_desist`, and command-line option constants.

Risks/notes:
- Fixed strategy selection is score-based; a strategy returning an unexpectedly high score can capture a drive.
- `drive_mark_discard` does not free mark records; ownership remains with callback/caller by contract.
