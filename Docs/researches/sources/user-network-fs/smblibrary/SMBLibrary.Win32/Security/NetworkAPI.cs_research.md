<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/NetworkAPI.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/NetworkAPI.cs

## Purpose
`NetworkAPI.cs` wraps NetAPI user and group enumeration calls used by Windows-integrated authentication.

## Important APIs, Types, And Functions
It defines NetAPI constants and marshaled structs `USER_INFO_0`, `USER_INFO_1`, and `LOCALGROUP_USERS_INFO_0`. It P/Invokes `NetApiBufferFree`, `NetUserEnum`, `NetUserGetInfo`, and `NetUserGetLocalGroups`. Public helpers are `EnumerateGroups`, `EnumerateAllUsers`, `EnumerateEnabledUsers`, `IsUserExists`, and `EnumerateNetworkUsers`.

## Control Flow
Enumeration methods call NetAPI with preferred maximum buffer sizes, marshal returned arrays by pointer arithmetic, collect names, and free NetAPI buffers. `IsUserExists` calls `NetUserGetInfo` level 0 and handles success/user-not-found specially. `EnumerateNetworkUsers` filters enabled users by membership in local groups `Users`, `Administrators`, or `Guests`.

## State And Persistence
No persistent state is stored. Native buffers are allocated by NetAPI and freed with `NetApiBufferFree` when entries are returned.

## Dependencies And Integration Points
It depends on `Netapi32.dll`, marshaling, and `Utilities`. `IntegratedNTLMAuthenticationProvider` calls `IsUserExists`; server UI or account listing code may use the enumeration helpers.

## Risks
Some methods only free buffers when `entriesRead > 0`; NetAPI may return a non-zero buffer with zero entries in edge cases. Pointer arithmetic uses `ToInt64`, which is generally safe but manually maintained. Group name filtering is English/localized-name dependent. Network/domain users are not comprehensively represented by local NetUser calls.

## Test Signals
No direct tests in this subset. Windows account enumeration and guest fallback behavior require platform integration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/NetworkAPI.cs -->
