# sources/sync-backup/bup/lib/bup/cmd/tick.py

## Purpose
`tick.py` sleeps until the next whole-second boundary. It is a small timing helper used to avoid timestamp-resolution races in tests or scripts.

## APIs and Control Flow
`main(argv)` rejects arguments, reads `time.time()`, computes the fractional remainder to the next integer second as `1 - (t - int(t))`, and sleeps that amount.

## State, Dependencies, Integration, Risks, Tests
It persists nothing and depends only on `time` and option parsing. It is conceptually related to the explicit one-second wait in `index.py` for timestamp race avoidance. Risks are minimal: if called exactly on a boundary it sleeps a full second, and system clock adjustments are not considered. Test signals include no-argument enforcement and elapsed sleep falling within expected bounds relative to the next second.
