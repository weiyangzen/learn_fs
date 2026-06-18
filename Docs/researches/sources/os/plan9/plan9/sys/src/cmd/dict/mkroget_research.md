# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/mkroget

This rc script builds the Roget dictionary data and index.

Key behaviors:
- Converts `roget-body.rtf` to text with `rtf2txt`.
- Drops the first 12 lines.
- Special-cases entries beginning `100. ` and `388a. ` by joining the following line.
- Writes processed dictionary text to `/lib/dict/roget`.
- Runs `mkindex -d roget`, sorts uniquely with folded-key/numeric-offset ordering, cleans spacing, and writes `/lib/dict/rogetindex`.

Notable implementation details:
- This is an install/build-time data-generation script for the Roget backend.
