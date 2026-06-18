# sources/user-network-fs/rclone/lib/buildinfo/osversion_windows.go

## Purpose
This Windows-only buildinfo file builds the user-facing OS version and kernel strings reported by rclone. It augments generic `gopsutil` host information with Windows registry release labels and architecture annotations, while normalizing noisy Windows kernel output.

## Important APIs, types, and functions
- `GetOSVersion() (osVersion, osKernel string)` is the exported entry point for Windows build information.
- `getRegistryVersionString(name string) string` reads string values such as `DisplayVersion` and `ReleaseId` from `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`.
- `regVersionKeyUTF16` caches the registry key path as a UTF-16 pointer for Win32 calls.

## Control flow
`GetOSVersion` first asks `host.PlatformInformation` for platform and version, then asks `host.KernelVersion` for the kernel. If the OS version already contains the kernel string, it removes the duplicate. It also collapses kernel strings of the form `major.minor.build.revision Build build.revision` when the build portion is repeated. Next it reads `DisplayVersion`, falling back to `ReleaseId`, and appends that friendly release name. Finally it reads `host.KernelArch`; 64-bit arches add `(64 bit)` to the OS version and append the raw arch to the kernel string.

## State and persistence behavior
The file has no persistent state. It reads live host and registry state each time `GetOSVersion` runs. Registry handles are opened per lookup and closed with `RegCloseKey`.

## Dependencies and integration points
The code depends on `github.com/shirou/gopsutil/v4/host` for platform/kernel/architecture probes and `golang.org/x/sys/windows` for registry access. It integrates with the wider buildinfo package as the Windows implementation of OS version reporting.

## Risks and edge cases
Registry access can fail due to permissions, missing keys, or non-standard Windows versions; failures intentionally degrade to partial host information. The registry buffer is sized from the reported byte length and interpreted as UTF-16, so type mismatches or malformed data would return odd strings rather than validated semantic versions. The kernel normalization regex is narrow and only handles one duplicated-build pattern.

## Test signals
No direct tests are in this subset. Coverage is likely indirect through version-reporting commands on Windows; non-Windows CI will not compile this file.
