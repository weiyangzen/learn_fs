# sources/sync-backup/bup/dev/with-tty

## Purpose
Runs a command under a pseudo-terminal using the platform `script(1)` command, preserving child exit status where possible.

## Important APIs, Types, and Functions
Supports `with-tty command [arg ...]`; probes `script -qec`, `script -q -c`, and `script -q /dev/null command` variants; rejects NetBSD up front.

## Control Flow
Validates args, tries known script invocation forms with a `true` command, verifies false returns nonzero for variants lacking `-e`, then runs the requested command through the supported form.

## State and Persistence Behavior
No persistent files beyond `/dev/null` script output target.

## Dependencies and Integration Points
Used by tests needing terminal behavior. Depends on non-POSIX `script` command variants.

## Risks and Test Signals
Risks are platform-specific `script` semantics, quoted command construction, and NetBSD unsupported behavior. Signal is correct child exit propagation and PTY allocation.
