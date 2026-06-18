# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/paths/SymlinkPathResolverSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/paths/SymlinkPathResolverSpec.groovy

Purpose: tests symlink-aware path resolution behavior. It exercises `SymlinkPathResolver` with mocked/stubbed share and file-link data to verify how symbolic-link targets are transformed into SMB paths and how relative/absolute target forms are handled.

State and persistence: transient path-resolution state only; no persistence. Dependencies are SMBJ path/share abstractions, symlink/reparse-point models, and Spock. Integration point is resolving server-side symlinks before file operations. Risks covered include incorrect target normalization, loops or unresolved links, and mixing UNC-style separators. Test signal is important for path correctness where servers expose symlinks.
