# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pfbtopfa

Shell wrapper converting binary Type 1 `.pfb` fonts to ASCII `.pfa`.

Behavior:

- Accepts `input.pfb [output.pfa]`; derives the output basename when omitted.
- Rejects other argument counts with usage text.
- Runs Ghostscript in no-display mode over `pfbtopfa.ps` with input and output paths.

The script is font conversion glue.
