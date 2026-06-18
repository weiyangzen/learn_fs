# sources/security-integrity/gocryptfs/tests/symlink_race/main.go

## Purpose
Standalone race reproducer that alternates a path between symlink and regular file while another goroutine opens and writes it, looking for unsafe symlink-following behavior.

## Important APIs, Types, And Functions
- `renameLoop` repeatedly creates a symlink to `/root/chmod_me`, renames it into place, creates a regular temp file, and renames that into place.
- `openLoop` repeatedly opens `symlink_race.test_file` with `O_RDWR`, writes `owned`, reads back, and exits nonzero if content appears.
- `main` starts `openLoop` and runs `renameLoop` forever.

## Control Flow
Two loops race on the same filename. One loop swaps file type through atomic renames; the other tries to open and modify the path, which can reveal time-of-check/time-of-use issues.

## State And Persistence
Creates and mutates `symlink_race.test_file` and `.tmp` in the current working directory indefinitely.

## Dependencies And Integration Points
Depends only on Go `os`, `syscall`, and filesystem rename/open semantics. It is intended to run inside a target mount.

## Risks And Edge Cases
It is destructive in the current directory and infinite. The target `/root/chmod_me` is hard-coded to expose privilege-sensitive symlink following if run with elevated access.

## Test Signals
The failure signal is printing unexpected content and exiting with status 1; otherwise it prints progress dots and transient errors.
