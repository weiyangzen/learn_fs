# sources/user-network-fs/rclone/backend/archive/base/base.go

Purpose: Provides a skeletal read-only archive Fs/Object implementation intended as common base code for concrete archivers, though its main read methods are placeholders.

Important APIs/types/functions: `Fs` stores wrapped Fs, wrapper, name, features, VFS, archive node, remote, prefix, and root. `New` builds a VFS, stats the archive object, sets features, and returns `*Fs`. Methods implement `fs.Fs`, `fs.UnWrapper`, and `fs.Wrapper`; `List`, `NewObject`, and `Object.Open` return internal `errNotImplemented`. Mutating methods return `vfs.EROFS`; hashes return none. `Object` exposes default remote/size/modtime/hash/update/remove behavior.

Control flow: `New` opens enough state to represent an archive file but does not parse a format. Consumers would embed or adapt this to implement format-specific listing and object reads.

State and persistence: Holds VFS and archive node handles plus path metadata. No writes are permitted through this base.

Dependencies and integration points: Depends on rclone `fs`, `hash`, and `vfs`. Shares design with concrete zip/squashfs implementations.

Risks: Placeholder methods make direct use invalid for real archivers. Default object `Size=-1` and `ModTime=time.Now()` are not suitable for stable listings.

Test signals: No direct tests visible in this subset. Concrete archivers duplicate rather than directly use most behavior.
