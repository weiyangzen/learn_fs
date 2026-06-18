<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/cltool.c -->
# sources/sync-backup/unison/src/uimac/cltool.c

Source read: complete file, 67 lines, 2115 bytes, sha256 `eec058c365f05e43`.

Purpose: Command-line launcher installed inside the Mac app bundle; it finds the GUI app through Launch Services and execs the real bundled `Unison` binary with the original arguments.

Important APIs/types/functions: Single `main` uses `LSFindApplicationForInfo`, `FSRefMakePath`, buffer concatenation with `/Contents/MacOS/Unison`, and `execv`.

Control flow: The tool resolves bundle id `edu.upenn.cis.Unison`, converts the app `FSRef` to a path, appends the executable suffix, replaces `argv[0]` with the absolute executable path, and calls `execv`. On lookup/path/exec failure it writes a user-facing stderr error and exits nonzero.

State and persistence behavior: No persistent state; it uses a fixed 1024-byte stack buffer for the app path.

Dependencies and integration points: Depends on CoreServices/ApplicationServices Launch Services and the app's Info.plist bundle identifier. It is compiled by the Mac UI Makefile with the Carbon framework.

Risks: Uses deprecated FSRef/Launch Services C APIs and a fixed path buffer. If the Launch Services database is stale, users must launch the app once from Finder. Bundle id changes break lookup.

Test signals: After installing/copying the app, run `cltool -version`, server mode, and a normal profile invocation; test renamed app bundles and overlong paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/cltool.c -->
