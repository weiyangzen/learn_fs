<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.conf -->
# sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.conf

## Purpose
Provides the default verbose-check input for `sestatus -v`.

## Important APIs, Types, And Functions
The file has two recognized sections: `[files]` and `[process]`. The C loader treats noncomment, nonblank lines under `[files]` as paths for `lgetfilecon`/`getfilecon` checks and lines under `[process]` as executable paths to locate in `/proc`.

## Control Flow
`sestatus` reads the file top to bottom, switches parser state on section headers, and records up to 50 entries for each section. The shipped file checks core login/shell/system binaries and common getty/sshd processes.

## State And Persistence
This is persistent host configuration under `/etc/sestatus.conf` when installed.

## Dependencies And Integration Points
Entries must match real filesystem paths and process executable symlink targets. Package layouts using `/usr` merge or alternate init/getty locations may need customization.

## Risks And Edge Cases
Stale paths cause missing context output. Process checks are exact executable-path matches, not service names. The file has no schema version, so parser compatibility depends on stable section names.

## Test Signals
Run `sestatus -v` with the installed file on systems with and without the listed paths/processes, and verify comments/blank lines are ignored.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.conf -->
