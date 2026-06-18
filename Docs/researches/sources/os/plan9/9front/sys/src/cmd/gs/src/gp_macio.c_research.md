# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macio.c

MacOS file, stdio, resource, path, and native-font platform implementation.

Key behavior:
- Converts between Mac `FSSpec` objects and colon-delimited HFS paths.
- Supplies a custom `getenv` for `GS_LIB`, deriving paths under the system Application Support folder.
- Installs a `macstdio` pseudo IODevice that patches `%stdin`, `%stdout`, and `%stderr` to route through the Ghostscript DLL callback.
- Opens printer output as a scratch file or regular file.
- Creates scratch files in the temporary folder using `tmpnam`, `FindFolder`, and `FSMakeFSSpec`.
- Reads Mac resource-fork data by type/id through `FSpOpenResFile` and `Get1Resource`.
- Provides a placeholder file enumeration implementation that never returns matches.
- Implements Mac path-combination helpers using `:` separators and Carbon volume root detection when available.
- Enumerates native fonts with Font Manager APIs, generating PostScript-like names and paths, including `%macresource%...#sfnt+id` references from FOND resources.

Notable dependencies:
- Classic MacOS/Carbon file, resource, folder, and font APIs.
- Ghostscript callback interface from `gsdll.h`.

Research notes:
- Comments explicitly say file enumeration is unsupported on Macintosh systems.
- Font enumeration caches the last font container and parsed FOND table to avoid reparsing.
- Several comments flag incomplete Unicode and LWFN handling.
