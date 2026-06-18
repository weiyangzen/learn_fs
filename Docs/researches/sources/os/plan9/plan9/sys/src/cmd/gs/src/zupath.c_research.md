# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zupath.c

## Purpose
Implements LanguageLevel 2 user-path operators and insideness tests for current paths or user paths.

## Public Surface
- Insideness: `ineofill`, `infill`, `instroke`, `inueofill`, `inufill`, `inustroke`.
- User path operations: `uappend`, `ucache`, `ueofill`, `ufill`, `upath`, `ustroke`, `ustrokepath`.
- Exported helper `make_upath`.
- Registered through `zupath_l2_op_defs`.

## Implementation Notes
- Insideness tests create a temporary clipping aperture and install `gs_hit_device` to detect whether painting hits.
- Coordinate tests use a one-pixel fixed rectangle; user-path tests preserve current path while clipping to an appended path.
- `inustroke` handles optional matrix operands and concatenates or returns identity as needed.
- User path opcode arrays support compact two-element form: operands array plus opcode string with repeat encoding.
- Ordinary executable user-path arrays are validated against a whitelist of path operators.
- `make_upath` enumerates a Ghostscript path, allocates an executable array, writes optional `ucache`, `setbbox`, and path construction operators.
- `upath_append` resets the current path, interprets compact or executable path arrays, and updates `current_point`.
- `ustrokepath` preserves and frees path storage carefully while replacing path with stroked outline.

## Dependencies
Depends on path, graphics-state, matrix, painting, fixed-point, dictionary, name, numeric-array, and device/hit-detection APIs.

## Risks and Notes
- User-path parsing executes only recognized operators and enforces exact argument counts.
- Temporary gsave/grestore and path preservation are critical to avoid changing current graphics state during tests.
- Compact user-path operand decoding depends on numeric-array format helpers.
- Filesystem relevance: none; graphics/path subsystem only.
