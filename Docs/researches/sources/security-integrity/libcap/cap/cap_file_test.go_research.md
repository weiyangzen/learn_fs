<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_file_test.go -->
# sources/security-integrity/libcap/cap/cap_file_test.go

## Purpose
Linux/go1.16 file-capability integration test for reading, writing, and removing `security.capability` xattrs.

## Important APIs, Types, And Functions
Uses `GetProc`, `GetFlag`, `Dup`, `SetFlag`, `SetProc`, `SetFile`, `GetFile`, `Cf`, `os.WriteFile`, `os.Symlink`, and `os.Chmod`.

## Control Flow
Skips if permitted `SETFCAP` is absent. Raises effective `SETFCAP`, creates a temp executable and symlink, asserts symlink writes fail, writes file capabilities to the real file, reads and compares them, removes them with nil `*Set`, then repeats on an unreadable file through the O_PATH fallback.

## State And Persistence Behavior
Temporarily raises process effective `SETFCAP` and restores the old capability set via defer. Persists xattrs on temp files and removes them before exit.

## Dependencies And Integration Points
Requires Linux, Go 1.16, xattr-capable filesystem, and permission to set file capabilities. Exercises `file.go` paths including symlink refusal and O_PATH fallback.

## Risks And Edge Cases
The test is skipped without privilege. It depends on filesystem xattr support and kernel file capability support. Incorrect cleanup could leave file caps in a temp dir until test cleanup.

## Test Signals
Signals are symlink write rejection, successful write/read comparison, successful nil removal, and successful set/read/remove on a chmod-0 file.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_file_test.go -->
