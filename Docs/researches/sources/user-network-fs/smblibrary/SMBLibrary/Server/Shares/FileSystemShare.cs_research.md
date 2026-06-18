<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/FileSystemShare.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/FileSystemShare.cs

## Purpose
Concrete disk-share implementation that binds a share name, an `INTFileStore`, and a caching policy, with event-driven authorization hooks.

## APIs, Types, and Functions
Constructors accept share name, file store, and optional `CachingPolicy`. Public methods `HasReadAccess()`, `HasWriteAccess()`, and `HasAccess()` raise `AccessRequested`. Properties expose `Name`, `FileStore`, and `CachingPolicy`.

## Control Flow, State, and Persistence
`HasAccess()` captures the event delegate, creates `AccessRequestArgs`, invokes subscribers, and returns `args.Allow`; without subscribers it returns true. The object stores the backing file store reference and policy but does not persist configuration.

## Dependencies and Integration
Used by tree-connect helpers, SMB2 file helpers, `SMBShareCollection`, and the sample UI. The backing store performs actual file operations and persistence.

## Risks and Test Signals
Risks include default-allow security, authorization decoupled from actual NTFS ACLs unless the backing store enforces them, public event handler ordering, and share-name immutability only by convention. Test no-handler access, denial handlers, read/write/read-write distinction, and use with different `INTFileStore` implementations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/FileSystemShare.cs -->
