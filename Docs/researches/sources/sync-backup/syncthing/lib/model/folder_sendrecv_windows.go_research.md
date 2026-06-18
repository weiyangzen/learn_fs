# sources/sync-backup/syncthing/lib/model/folder_sendrecv_windows.go

Purpose: this Windows implementation provides ownership synchronization for `sendReceiveFolder` and helper functions for resolving Windows user or group names into IDs accepted by the filesystem `Lchown` abstraction.

Important APIs: `syncOwnership(file *protocol.FileInfo, path string) error` applies `protocol.FileInfo.Platform.Windows.OwnerName` when present. `lookupUserAndGroup(name string, group bool) (string, string, error)` resolves either a user ID or group ID and leaves the other field blank, matching `Lchown` expectations. `lookupWithoutDomain(name string, lookup func(string) (string, error)) (string, error)` retries qualified names without the `DOMAIN\` prefix.

Control flow: `syncOwnership` exits when Windows platform data or owner name is missing. It logs the requested owner and group flag, resolves the principal using `lookupUserAndGroup`, logs the resolved IDs, and calls `f.mtimefs.Lchown(path, usid, gsid)`. If the platform metadata marks the owner as a group, group lookup is used; otherwise user lookup is used. The lookup helper tries the full name first and then, only for a two-part backslash-qualified name, retries the user or group portion after the backslash.

State and persistence behavior: the function has no database state. Its persistent effect is an ownership change on the filesystem object. Failed lookups stop before filesystem mutation and return contextual errors such as `lookup user <name>` or `lookup group <name>`.

Dependencies and integration points: it uses Go `os/user`, `strings`, `fmt`, Syncthing logging, `protocol.PlatformData`, and the folder's `mtimefs`. It integrates with the same platform-data application path as the Unix implementation, but must bridge Windows account naming conventions to the filesystem interface.

Risks: Windows account names can include domains, local machine prefixes, groups, and localized names. The retry logic only handles exactly one backslash separator, so unusual forms may fail. The function returns lookup errors instead of silently falling back, unlike the Unix version; this stricter behavior can surface as pull errors. Correctness also depends on the filesystem backend interpreting blank user or group fields the same way the function expects.

Test signals: direct tests for `lookupUserAndGroup` are not present in this subset. Windows send/receive coverage exists for symlink-over-existing-file behavior, but ownership resolution relies mainly on platform-specific runtime coverage and fake filesystem behavior elsewhere.
