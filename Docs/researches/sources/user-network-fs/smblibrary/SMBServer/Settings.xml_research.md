<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Settings.xml -->
# sources/user-network-fs/smblibrary/SMBServer/Settings.xml

## Purpose
Sample XML configuration consumed by the SMB server UI for independent NTLM users and disk share definitions.

## APIs, Types, and Functions
The XML root is `Settings` with `Shares/Share` entries (`Name`, `Path`, `ReadAccess Accounts`, `WriteAccess Accounts`) and `Users/User` entries (`AccountName`, `Password`).

## Control Flow, State, and Persistence
`SettingsHelper` loads this file from the executable directory at start time. The sample defines a `Shared` share at `C:\Shared`, read access for `*`, write access for `Admin,Test`, and users `Admin`, `Guest`, and `Test` with plain-text passwords.

## Dependencies and Integration
Used by `SettingsHelper.ReadSharesSettings()` and `ReadUserSettings()` when integrated Windows authentication is disabled.

## Risks and Test Signals
Risks include plain-text credentials, Windows-specific sample path, permissive wildcard read access, no schema validation, and deployment mismatch if the file is not copied beside the executable. Test parsing, wildcard mapping, missing attributes, nonexistent share path, and independent-auth login for sample users.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Settings.xml -->
