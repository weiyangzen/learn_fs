# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSPath.java

Source read signal: reviewed complete local file (114 lines, 3548 bytes).

## Purpose
`DFSPath.java` covers DFS path model. parses UNC/DFS paths into components, converts `SmbPath` to DFS form, replaces prefixes with referral targets, identifies SYSVOL/NETLOGON and IPC paths, and renders back to backslash paths.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructors split leading double-backslash or single-backslash paths; `replacePrefix()` swaps a prefix for target components and appends the remaining suffix; `from()` builds components from host/share/path.

## State and persistence
Holds immutable reference to a component list, though caller-supplied lists are not defensively copied.

## Dependencies and integration points
Integrates with DFS referral cache, domain cache interlink detection, and SMB path resolution.

## Risks
Empty or one-character path strings can fail due to direct `charAt`; case checks for SYSVOL/NETLOGON/IPC are exact uppercase only.

## Test signals
Signals are DFS integration tests and unit tests for prefix replacement and path rendering.
