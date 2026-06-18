# File Research: sources/windows/winfsp/src/dll/np.c

This file implements the Windows Network Provider API for WinFsp network-style filesystems.

Key responsibilities:
- `NPGetCaps` advertises connection, enumeration, provider type, spec version, and startup capabilities.
- Parses local drive names and WinFsp remote names of the form `\\Class\Instance`.
- Calls launcher pipe commands for start/stop/info operations, optionally allowing impersonation for suitable launcher records.
- Reads launcher registry records to determine auth package, credential requirements, and impersonation behavior.
- Supports credential prompting via CredUI, optional credential manager reads/writes, and password/user-password credential modes.
- `FspNpCheckRemoteVolume` probes an existing UNC path and verifies it is a WinFsp volume via `FSP_FSCTL_QUERY_WINFSP`.
- `NPGetConnection` maps a local drive letter back to a WinFsp remote name by comparing DOS device targets to the WinFsp network volume list.
- `NPAddConnection` validates names, gathers credentials, starts the filesystem through the launcher, waits for the root path to become accessible, and handles already-running instances.
- `NPAddConnection3` adds interactive prompting/retry behavior and optional credential persistence.
- `NPCancelConnection` resolves a drive or remote name and asks the launcher to stop the instance.
- `NPGetUniversalName` converts local drive paths to UNC/universal name structures.
- `NPOpenEnum`, `NPEnumResource`, and `NPCloseEnum` enumerate connected/context network resources by walking the WinFsp network volume list and associating drive letters where possible.
- `FspNpRegister` creates service/network-provider registry keys, writes provider metadata/path/device name, and inserts `WinFsp.Np` into `ProviderOrder` first.
- `FspNpUnregister` removes the provider from `ProviderOrder` and deletes its service registry tree.

Filesystem relevance:
- This is the integration layer that makes WinFsp UNC-style filesystems appear as Windows network resources.
- It connects the launcher service, credential UI/storage, MPR network-provider callbacks, and WinFsp volume enumeration.
