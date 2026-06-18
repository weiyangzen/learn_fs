## sources/sync-backup/syncthing/lib/fs/basicfs.go

Purpose: Implements the core `basic` filesystem by rooting relative paths under a configured OS directory and delegating most operations to the Go `os` package.

Important APIs/types/functions: `FilesystemTypeBasic`; filename errors; `OptionJunctionsAsDirs`; `BasicFilesystem`; `newBasicFilesystem`; `rooted`; methods `Chmod`, `Chtimes`, `Mkdir`, `MkdirAll`, `Lstat`, `RemoveAll`, `Rename`, `Stat`, `DirNames`, `Open`, `OpenFile`, `Create`, `Walk`, `Glob`, `Usage`, `Type`, `URI`, `Options`, `SameFile`, `underlying`; `basicFile`; `basicFileInfo`; `longFilenameSupport`; `WatchEventOutsideRootError`.

Control flow: Registration installs a factory for type `basic`. Construction normalizes root, expands tilde, absolutizes when possible, applies Windows long-path prefix, initializes user/group caches, and applies options. Operations call `rooted` to canonicalize and join paths safely before invoking OS calls. `OpenFile` adds platform `alwaysOpenFlags`; `Lstat` delegates to platform-specific `underlyingLstat`; `Glob` unroots matches; `SameFile` only compares basic file info values.

State and persistence: Holds root path, options, junction behavior, and one-hour user/group caches. It manipulates real filesystem state under the root via OS calls.

Dependencies and integration points: Implements Syncthing `Filesystem`; integrates with platform-specific `basicfs_*` files, disk usage via gopsutil, build flags, and higher-level walking/copy/xattr code.

Risks: Root canonicalization is security-sensitive; any bypass could escape the shared folder. `RemoveAll` and `Rename` operate on rooted paths and therefore have high destructive impact if rooting is wrong. `Walk` intentionally returns not implemented because walking is handled elsewhere.

Test signals: Broader `basicfs_test.go` outside this item covers many operations; platform files in this subset add targeted behavior.
