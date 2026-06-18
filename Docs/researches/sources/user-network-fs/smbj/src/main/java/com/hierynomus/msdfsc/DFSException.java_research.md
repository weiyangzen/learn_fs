# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSException.java

Source read signal: reviewed complete local file (33 lines, 1015 bytes).

## Purpose
`DFSException.java` covers DFS exception type. specializes smbj exception handling for DFS resolution/referral errors.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructors pass message/cause/status context to the parent exception type.

## State and persistence
No state beyond exception fields.

## Dependencies and integration points
Used by DFS client code around referral lookup and path replacement failures.

## Risks
Too-generic messages make multi-target DFS fallback hard to diagnose.

## Test signals
Signals are DFS tests surfacing meaningful failures.
