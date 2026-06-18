# File Research: sources/virtualization/spdk/app/iscsi_tgt/iscsi_tgt.c

## Purpose
Minimal executable wrapper for the SPDK iSCSI target app.

## Main Entry Points
- `iscsi_parse_arg()` handles `-b` daemon mode.
- `iscsi_usage()` prints the iSCSI-specific option.
- `spdk_startup()` optionally dumps memzones when `MEMZONE_DUMP` is set.
- `main()` initializes app opts, parses SPDK and app arguments, optionally daemonizes, starts SPDK app framework, finalizes, and returns status.

## Internal Mechanics
The app name is `iscsi`. It relies on linked event subsystems to initialize the actual iSCSI target functionality. `daemon(1, 0)` is called after argument parsing and before `spdk_app_start()` when `-b` is supplied.

## Dependencies
Uses SPDK app/event/env/log APIs and includes `iscsi/iscsi.h` from SPDK's internal library path.

## Filesystem/Block Relevance
This is the process entry point for serving SPDK bdev-backed logical units through iSCSI.

## Risks and Notes
- No custom shutdown callback is installed.
- Failure to daemonize exits immediately.
- Most target behavior is in linked libraries, not this wrapper.
