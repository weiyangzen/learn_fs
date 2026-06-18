# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/version.h

Purpose: `version.h` defines the e2fsprogs version and release date strings used by programs in this vendored e2fsprogs-libs snapshot.

Important APIs, types, and functions: macros `E2FSPROGS_VERSION "1.41.14"` and `E2FSPROGS_DATE "22-Dec-2010"`.

Control flow: header-only macro definitions; no runtime control flow.

State and persistence: compile-time constants become embedded in binaries that include this header.

Dependencies and integration points: included by e2fsprogs utilities outside this work item for version reporting. It aligns with template substitutions used by manpages and package metadata.

Risks: stale version strings can mislead diagnostics and packaged artifacts. Because this is a vendored snapshot inside xfstests-bld, version drift may be intentional.

Test signals: compile a version-reporting utility and check output; compare with generated package/manpage metadata when building the snapshot.
