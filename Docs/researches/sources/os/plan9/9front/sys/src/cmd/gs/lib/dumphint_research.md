# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/dumphint

Shell wrapper for formatting or dumping linearized PDF hint information with Ghostscript `dumphint.ps`.

Behavior:
- Starts with `OPTIONS="-dSAFER -dDELAYSAFER"` and appends leading `-*` arguments.
- Requires exactly one positional `input.pdf`.
- Runs Ghostscript quietly with `-dNODISPLAY`, collected options, `dumphint.ps`, and the input path.

Filesystem relevance:
- Wrapper reads a PDF through Ghostscript; no filesystem implementation logic.
