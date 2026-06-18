# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ccfont.h

This header defines support types and procedure interfaces for fonts compiled into C.

Key responsibilities:
- Includes Ghostscript core/interpreter headers needed by generated compiled-font C files.
- Defines typed `ref_` initializer structures and helper macros for boolean, integer, null, and real refs.
- Defines `charindex` for encoding and character index pairs.
- Documents `cfont_string_array`, a compact byte-string representation for mostly-string arrays, including string/name/null/token-encoded elements.
- Defines `cfont_dict_keys`, describing dictionary key metadata and protection attributes.
- Defines `cfont_procs`, a procedural interface used by generated font initialization code to create dictionaries, arrays, names, and refs without direct external symbol dependencies.
- Defines `ccfont_proc` and `ccfont_fproc` function signatures for compiled font providers.
- Declares `ccfont_fprocs`, which returns the compiled font table.
- Defines `ccfont_version 19` for compatibility checking.

Dependencies and interfaces:
- Depends on `stdpre.h`, `gsmemory.h`, `iref.h`, `ivmspace.h`, and `store.h`.
- Designed to support both statically compiled fonts and third-party shared-library compiled fonts.

Notable implementation details:
- Header-only interface and data layout definitions.
- No filesystem logic.
- Its design avoids external references to improve sharability of compiled font objects.

Research classification: Ghostscript compiled-font ABI/header.
