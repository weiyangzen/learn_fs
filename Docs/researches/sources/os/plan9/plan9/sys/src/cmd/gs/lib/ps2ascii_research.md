# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ascii

Shell wrapper for extracting ASCII text from PostScript.

Behavior:

- Uses Ghostscript with `-q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE`.
- Accepts zero, one, or two arguments:
  - no arguments: stdin to stdout,
  - one input file: text to stdout,
  - input plus output: redirects text to the output file.
- Runs `ps2ascii.ps` and terminates with `-c quit`.
- Installs a trap to remove `_temp_.err` and `_temp_.out`, though this wrapper itself does not create them directly.

This is text-extraction command glue.
