<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/Enums/CachingPolicy.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/Enums/CachingPolicy.cs

## Purpose
Defines share client-side caching policy values used when advertising SMB1 optional support flags and SMB2 share flags.

## APIs, Types, and Functions
`CachingPolicy` enum values are `ManualCaching`, `AutoCaching`, `VideoCaching`, and `NoCaching`.

## Control Flow, State, and Persistence
No runtime flow or state. Values are stored in `FileSystemShare` and translated by SMB1/SMB2 tree-connect helpers.

## Dependencies and Integration
Integrated with `FileSystemShare.CachingPolicy`, `SMB1.TreeConnectHelper.GetCachingSupportFlags()`, and `SMB2.TreeConnectHelper.GetShareCachingFlags()`.

## Risks and Test Signals
Risk is semantic mismatch between enum names and protocol flag mappings, especially offline-file reintegration behavior. Test tree-connect responses for each policy in SMB1 and SMB2 and default behavior for unknown values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/Enums/CachingPolicy.cs -->
