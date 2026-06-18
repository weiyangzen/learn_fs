<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/version.go -->
# sources/sync-backup/git-lfs/config/version.go

## Research

`version.go` defines build/version metadata. `Version` is `3.7.0`; variables `GitCommit`, `VersionDesc`, and `Vendor` can be populated at build time. `init` defaults `Vendor` to `GitHub`, appends Git commit metadata if present, and constructs a user-agent-like `VersionDesc` containing version, vendor, OS, architecture, Go runtime, and optional commit.

State is package-global and initialized once. Integration includes CLI version output and HTTP user-agent/version reporting elsewhere. Risks are build flag drift, runtime `strings.Replace(runtime.Version(), "go", "", 1)` assumptions, and global variables being mutable after init. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/version.go -->
