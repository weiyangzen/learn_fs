# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfrsd.c

## Purpose
Provides internal support for `ReusableStreamDecode`: parameter normalization and creation of reusable streams from strings, bytes, seekable files, and certain subfile filters.

## Key Functions
- `zrsdparams()` normalizes `Filter` and `DecodeParms` into arrays/null and validates decode filter names.
- `zreusablestream()` validates reusable sources and delegates to string or file stream constructors.
- `make_rss()` creates a reusable string stream over a string or bytes object.
- `make_rfs()` reopens a named file and wraps a subfile slice as a reusable stream.

## Important Behavior
- Filter names must end in `Decode`.
- `DecodeParms` must be null, a dictionary for a single filter, or an array matching the filter array length.
- Reusable file sources must be readable and seekable.
- A `SubFileDecode` source is reusable only when its `EODString` is empty; offsets and lengths are adjusted from `skip_count`, buffered bytes, and count.
- `%stdin%`-like device-only streams cannot be reopened as reusable files.

## Research Notes
The surrounding reusable-stream construction is mostly in PostScript; this file handles the C-level source inspection and stream reopening details.
