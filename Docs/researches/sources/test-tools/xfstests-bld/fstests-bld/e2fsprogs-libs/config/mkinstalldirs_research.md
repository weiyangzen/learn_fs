<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs

Source read: complete file, 40 lines, 722 bytes, sha256 `208dfecf8a8761b964838808394c09ca887e23421df370ff65dec7773b2f345c`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs_research.md`.

Purpose: public-domain helper script that creates one or more directory hierarchies portably for old make/install flows.

Important APIs/types/functions: accepts directories as positional arguments; tracks `errstatus`; uses `sed` to split each path into components; calls `mkdir` for missing intermediate paths; prefixes `./` when a component path would start with `-`.

Control flow: for each requested path, builds a shell argument list of path components, iteratively appends each component to `pathcomp`, creates missing directories, records mkdir failure if the directory still does not exist, and exits with accumulated status.

State and persistence behavior: creates directories in the filesystem and prints `mkdir PATH` for each creation. No other persistent state.

Dependencies and integration: used by configure/make install rules through `MKINSTALLDIRS` when `install-sh -d` or native `mkdir -p` is unavailable. Depends on POSIX shell, `sed`, and `mkdir`.

Risks: line-oriented path splitting is not safe for whitespace/newlines in paths. Concurrent creators can race but the post-mkdir directory existence check tolerates many benign races. It does not set modes or ownership.

Test signals: direct invocation with nested relative and absolute paths should create all components and return zero. Failure tests should use unwritable parents and leading-dash component names.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs -->
