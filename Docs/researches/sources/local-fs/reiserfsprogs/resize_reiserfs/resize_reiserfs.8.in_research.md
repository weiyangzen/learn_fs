# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.8.in

Manual page template for `resize_reiserfs`.

Major contents:
- Documents syntax: `resize_reiserfs [-s [+|-]size[K|M|G]] [-j dev] [-fqv] device`.
- Explains offline resize behavior and online growth support.
- Warns that the tool does not resize the underlying partition/device.
- Provides shrink workflow: unmount, shrink filesystem, then shrink device.
- Describes options for size, journal device, force, quiet, and verbosity.
- Lists return values and an example shrink session.
- References `cfdisk(8)`, `reiserfsck(8)`, and `debugreiserfs(8)`.

Dependencies and interactions:
- Version placeholder `@PACKAGE_VERSION@` is filled by the build system.
- Installed by `resize_reiserfs/Makefile.am`.

Risks and notes:
- The return value section says `-1` for failure, while C `main()` typically returns positive `1` for many failures.
- Option text says `-f` skips checks, while code mostly uses force for confirmations and some checks remain enforced.
