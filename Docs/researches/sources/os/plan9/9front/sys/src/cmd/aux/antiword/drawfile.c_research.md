# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/drawfile.c

RISC OS Drawfile utility implementation for Antiword.

Important behavior:
- Provides custom `os_error` generation for Drawfile validation errors.
- Wraps RISC OS SWIs for Drawfile bounding-box and rendering operations.
- `Drawfile_CreateDiagram()` initializes a Drawfile header with tag `Draw`, version 201.0, creator string, and bounding box.
- `Drawfile_AppendObject()` appends an object to diagram memory, optionally rebinding the overall diagram bounding box based on object type.
- `Drawfile_RenderDiagram()` builds a scaling/translation transform and invokes `DrawFile_Render`.
- `Drawfile_VerifyDiagram()` validates the diagram header and each object size/type, requiring font table before fonted text and checking text/path/sprite/JPEG consistency.
- `Drawfile_QueryBox()` asks the Drawfile system for bounds and optionally converts draw units to screen units.

Filesystem/output relevance:
- Owns the low-level append/verify/render mechanics for generated Drawfile documents.
