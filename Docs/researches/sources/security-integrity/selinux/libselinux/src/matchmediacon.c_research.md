<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchmediacon.c -->
# sources/security-integrity/selinux/libselinux/src/matchmediacon.c

## Purpose
Looks up the default SELinux context for removable media names using the configured media contexts file.

## Important APIs, Types, And Functions
`matchmediacon()` opens `selinux_media_context_path()`, scans whitespace-separated records, matches the first token against `media`, and translates the remainder from raw to translated context.

## Control Flow
The function reads line by line, trims a trailing character, skips leading whitespace and empty entries, splits the media key from the context, and stops on the first exact match.

## State And Persistence Behavior
No persistent state is changed. It reads a policy configuration file and allocates the returned context for the caller.

## Dependencies And Integration Points
Uses config path resolution, `selinux_raw_to_trans_context()`, unlocked stdio, and `PATH_MAX` line buffering.

## Risks And Test Signals
Risks include fixed line length, simplistic parsing, and the trailing-character trim condition. Tests should cover missing file, blank/comment-like records, long lines, missing contexts, exact media matches, no match, and translation failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchmediacon.c -->
