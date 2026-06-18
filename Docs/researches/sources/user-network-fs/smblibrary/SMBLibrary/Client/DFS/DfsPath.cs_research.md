<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsPath.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsPath.cs

## Purpose
`DfsPath` is a small UNC path model for DFS referral rewriting and share classification.

## Important APIs and Types
The constructor parses UNC-like strings into slash/backslash-delimited components. `ToUncPath()` and `ToString()` emit a canonical `\\server\share...` form. `ReplacePrefix()` rewrites case-insensitive path prefixes. Properties expose `ServerName`, `ShareName`, `HasOnlyOneComponent`, `IsSysVolOrNetLogon`, and `IsIpc`.

## Control Flow
Construction rejects null, empty, or componentless paths. Replacement verifies the old prefix length and component equality, then concatenates the new prefix and remaining suffix; non-matches return the original object.

## State, Dependencies, and Integration
State is an internal component list. DFS referral resolution can use it to convert namespace paths to referral target paths and classify special shares.

## Risks and Test Signals
`ServerName` assumes at least one component, guaranteed only through constructors. Returning `this` on non-match means callers should not assume a new object. Tests should cover slash variants, case-insensitive prefix replacement, one-component paths, IPC$/SYSVOL/NETLOGON detection, and invalid input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsPath.cs -->
