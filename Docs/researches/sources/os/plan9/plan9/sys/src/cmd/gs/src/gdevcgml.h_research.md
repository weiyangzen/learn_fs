# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.h

Public interface for the local CGM-writing library.

Key contents:
- Declares opaque `cgm_state` and allocator callback structure.
- Defines coordinate, VDC, point, RGB, color, string, precision, and other CGM data types.
- Defines enum types for CGM VDC type, scaling, color selection, line/marker/edge specification modes, transparency, clipping, line/marker/text/fill/edge styles, arc closure, cell representation, and aspect source flags.
- Defines result codes: OK, wrong state, out of range, I/O error, and out of memory.
- Defines metafile element, picture element, and update-mask structures/constants.
- Declares API functions for initialization/termination, metafile lifecycle, picture lifecycle, control elements, graphical primitives, and attribute elements.

Important behavior:
- Names mostly mirror CGM standard element names, with American spellings for color/center.
- The API supports direct and indexed color, integer and real VDCs, packed cell arrays, primitive geometry, text, color tables, and aspect source flags.
- Some CGM features are acknowledged but not represented, such as character set list, character coding announcer, and pattern table.

Dependencies:
- Requires Ghostscript base types such as `byte`, `uint`, `bool`, and `FILE`.
- Implemented by `gdevcgml.c` with internal state from `gdevcgmx.h`.

Notable risks:
- The public API exposes many CGM concepts but the implementation only partially validates/implements them.
- Several fields are raw pointers into caller-owned memory, such as font lists, element lists, and strings; lifetime must outlive use by the writer state where stored.
- Function naming includes `cgm_ALT_CHARACTER_SET_INDEX` because older VAX DEC C had a 31-character name limit.
