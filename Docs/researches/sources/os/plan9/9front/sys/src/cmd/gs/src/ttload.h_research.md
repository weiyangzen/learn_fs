# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.h

Public declarations and stream-access macros for TrueType table loading.

Key points:
- Declares many FreeType-style table loader entry points:
  - directory, maxp, gasp, head, hhea, loca, name, CVT, cmap, hmtx, programs, OS/2, post, hdmx, arbitrary table reads
  - name and hdmx cleanup helpers
- In this group, only maxp/CVT/program loading is implemented in `ttload.c`; other declarations are part of the broader FreeType-derived interface.
- Defines reader macros used by loaders:
  - `GET_Byte`
  - `GET_UShort`
  - `GET_Short`
  - `GET_Long`
  - `GET_ULong`
- Provides legacy stream/frame helper macros for `TT_CONFIG_REENTRANT` and non-reentrant/thread-safe builds.
- Exposes file-position, seek, skip, read, read-at, frame access, and frame-forget macros in the old FreeType style.

Dependencies and interactions:
- Includes `ttcommon.h`.
- Depends on FreeType-style stream APIs such as `TT_Use_Stream`, `TT_Access_Frame`, `TT_File_Pos`, `TT_Seek_File`, and related functions where those legacy paths are compiled.
- The current `ttload.c` uses the newer Ghostscript `ttfReader` macros at the top of this header.

Research relevance:
- This is the loader-facing API and portability shim connecting FreeType table-loader idioms to Ghostscript’s font reader abstraction.
