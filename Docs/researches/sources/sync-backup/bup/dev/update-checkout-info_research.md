# sources/sync-backup/bup/dev/update-checkout-info

## Purpose
Generates checkout metadata containing the current Git commit, commit date, and dirty status.

## Important APIs, Types, and Functions
Uses `pwd -P`, validates `lib/bup/bupsplit.c`, checks `.git`, runs `git status --porcelain -uno`, `git log -1 --pretty`, and writes through `dev/refresh`.

## Control Flow
Requires one destination path. If not in a Git checkout, removes the destination. Otherwise writes Python-style assignments `commit=`, `date=`, and `modified=` to the destination only when changed.

## State and Persistence Behavior
Creates/updates or removes the destination checkout info file, usually `lib/bup/checkout_info.py`.

## Dependencies and Integration Points
Called by `GNUmakefile`; installed as source info when present.

## Risks and Test Signals
Risks are dirty-state sensitivity and branchless/source-archive builds. Signals are generated metadata matching Git state and idempotent refresh behavior.
