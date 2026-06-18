# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_profile.c

This file implements `/dev` namespace profiles for non-global-zone sdev instances. Profiles define which global `/dev` names appear in a zone, which names are excluded, which symlinks are created, and which global devices are mapped under alternate names.

Profile rule types:
- Include
- Exclude
- Map
- Symlink

Key routines:
- `prof_getattr()` obtains attributes from the shadow backing store, creates shadow directories as needed, or derives default device attributes from devfs/global vnode state.
- `prof_mknode()` creates profile-visible sdev nodes and applies glob patterns to newly created directories.
- `prof_make_dir()` creates/intersects profile directories with corresponding global `/dev` directories.
- `prof_lookup_globaldev()` looks up a device in the global `/dev` origin and creates a visible node under the local name.
- `prof_make_symlinks()`, `prof_make_maps()`, and `prof_make_names()` materialize profile rules into directory contents.
- `prof_name_matched()` evaluates include/exclude and directory-glob rules.
- `walk_dir()` reads a directory and applies a callback to each non-dot entry.
- `prof_zone_matched()` applies a final zone-property check for `SDEV_ZONED` directories.
- `prof_filldir()` rebuilds directory contents when generation counters or build flags indicate stale contents.
- `process_rule()` parses paths and installs rules at the correct directory level.
- `sdev_process_profile()` consumes the packed profile nvlist entries.
- `prof_lookup()` performs lookup within a profiled directory, triggering `prof_filldir()` on cache miss.
- `devname_profile_update()` copies in the packed nvlist, finds the matching mounted sdev instance by mount point, and applies the profile.

The file depends on nvlist profile formats from libdevinfo/modctl, global `/dev` origins in `sdev_origins`, sdev cache/node helpers, pathname traversal, and devfs default attribute lookup.

Risk areas:
- Profile updates depend on first nvpair being `SDEV_NVNAME_MOUNTPT`.
- Include/exclude glob rules can recurse through existing directory contents.
- Global-zone peeking into zone `/dev` has a noted limitation for `SDEV_ZONED` property checks.
