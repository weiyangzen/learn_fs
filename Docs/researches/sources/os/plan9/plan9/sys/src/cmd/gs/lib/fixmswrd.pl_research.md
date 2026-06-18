# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/fixmswrd.pl

Perl filter that patches Microsoft Word printer-driver PostScript so older Ghostview can view pages independently.

Problem addressed:

- Word-generated DSC may open a procset dictionary outside page sections and close it in the trailer.
- Page viewers that isolate pages miss that dictionary context.

Behavior:

- Accepts `[-v] [file [output-file]]`, otherwise reads stdin and writes stdout.
- Reads and preserves header comments, adding `%LOCALGhostviewPatched` before `%%EndComments` unless already present.
- Detects procset/dictionary names from `%%BeginResource: procset ...` or older `%%BeginProcSet: ...`.
- Removes the original global `dict begin` line and trailer `end` line.
- Inserts `dict begin` after each `%%Page:` and `end` after each `showpage`.
- If the marker is already present, passes input through unchanged.

This is PostScript structure repair tooling; it does not touch Ghostscript internals.
