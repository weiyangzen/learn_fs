# sources/security-integrity/gocryptfs/tests/stress_tests/fsstress.collect-crashes.sh

## Purpose
Operator helper for repeatedly running `fsstress-loopback.bash` on an ext4 ramdisk and collecting bounded crash/debug logs.

## Important APIs, Types, And Functions
- Sets working directory to a developer GOPATH checkout path.
- `TMPDIR=/mnt/ext4-ramdisk` is required and write-tested.
- Loops up to 1000 times, capturing the last 1,000,000 lines of DEBUG fsstress output into timestamped logs.

## Control Flow
The script creates a log directory under `/tmp/$$`, removes old fsstress temp dirs, runs the loopback stress script with `DEBUG=1`, and pipes output through `tail` to cap each log file.

## State And Persistence
Writes logs under `/tmp/<pid>` and deletes fsstress temp dirs under the ramdisk before each run.

## Dependencies And Integration Points
Depends on a specific checkout location, writable ext4 ramdisk, and the fsstress loopback script.

## Risks And Edge Cases
The hard-coded path makes it non-portable. Each log can still be large, and the script does not stop after a successful no-crash run unless the child exits.

## Test Signals
Signals are collected logs for postmortem analysis; skipped existing log names avoid overwriting prior captures.
