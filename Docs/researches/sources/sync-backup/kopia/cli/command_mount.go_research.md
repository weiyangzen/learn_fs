# sources/sync-backup/kopia/cli/command_mount.go

## Purpose
Repository mount command that exposes a snapshot/object path through FUSE or WebDAV, with browse, tracing, cache, and mount-option controls.

## APIs, Types, and Functions
Important APIs include types `commandMount`; functions/methods `setup`, `newFSCache`, `run`; Kingpin command(s) mount: Mount repository object as a local filesystem.; flags browse: Open file browser, trace-fs: Trace filesystem operations, fuse-allow-other: Allows other users to access the file system., fuse-allow-non-empty-mount: Allows the mounting over a non-empty directory. The files in it will be shadowed by the freshly created mount., webdav: Use WebDAV to mount the repository object regardless of fuse availability., max-cached-entries: Limit the number of cached directory entries, max-cached-dirs: Limit the number of cached directories; arguments path: Identifier of the directory to mount., mountPoint: Mount point.

## Control Flow, State, and Persistence
Control flow registers command(s) mount: Mount repository object as a local filesystem., binds flags browse: Open file browser, trace-fs: Trace filesystem operations, fuse-allow-other: Allows other users to access the file system., fuse-allow-non-empty-mount: Allows the mounting over a non-empty directory. The files in it will be shadowed by the freshly created mount., webdav: Use WebDAV to mount the repository object regardless of fuse availability., max-cached-entries: Limit the number of cached directory entries, max-cached-dirs: Limit the number of cached directories, accepts arguments path: Identifier of the directory to mount., mountPoint: Mount point, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters, live mounted filesystem state and cache entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/skratchdot/open-golang/open, github.com/kopia/kopia/fs, github.com/kopia/kopia/fs/cachefs, github.com/kopia/kopia/fs/loggingfs, github.com/kopia/kopia/internal/mount, github.com/kopia/kopia/repo, github.com/kopia/kopia/snapshot/snapshotfs. It integrates with Kopia repository internals such as kopia/fs, kopia/fs/cachefs, kopia/fs/loggingfs, kopia/internal/mount, kopia/repo, kopia/snapshot/snapshotfs plus external packages context, github.com/pkg/errors, github.com/skratchdot/open-golang/open.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
