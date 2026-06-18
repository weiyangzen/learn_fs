# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.h

Public interface for the CGM-writing library.

Key contents:
- Abstract `cgm_state` and allocator callback types.
- CGM scalar, coordinate, point, color, precision, and string types.
- Enumerations for VDC type, scaling, color selection, line/marker/edge modes, transparency, clipping, text settings, fill styles, hatch indexes, arc closure, polygon edge visibility, cell representation, and aspect source flags.
- `cgm_result` error/result enum.
- Metafile and picture element structs plus bitmask flags for selective emission.
- Public prototypes for initialization, termination, metafile elements, picture elements, control elements, graphical primitives, and attribute elements.

Notable dependencies:
- Uses Ghostscript-style `uint`, `byte`, and `bool` types supplied by included compilation context rather than declaring them locally.

Research notes:
- The header names API functions after CGM standard elements, with shortened alternate-character-set naming for legacy VAX DEC C symbol length limits.
- It is a serialization API, not a rendering or parsing API.
