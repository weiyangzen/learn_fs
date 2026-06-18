# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.c

This file provides RISC OS Drawfile helper routines for creating, appending, rendering, validating, and querying diagrams.

Key behavior:
- Maps local Drawfile validation error codes to `os_error` structures.
- Calls RISC OS SWIs for bounding-box calculation and rendering.
- Initializes Drawfile headers with tag `Draw`, version 201.0, creator, and bounding box.
- Appends objects to diagram memory and optionally expands the diagram bounding box.
- Verifies text, path, sprite, JPEG, font-table, object-size, and diagram-header validity.
- Queries diagram bounding boxes and optionally converts Draw units to screen units.

Important details:
- Only a subset of object types is accepted by verification: font table, text, path, sprite, and JPEG.
- Text verification rejects control characters.
- Path verification requires at least one line and an end marker.

Filesystem relevance:
- Indirect: validates and renders converted output objects, not source file storage.
