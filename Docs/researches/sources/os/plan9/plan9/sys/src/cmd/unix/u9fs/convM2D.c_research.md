# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2D.c

Parses 9P stat message bytes into a `Dir`.

Functions:
- `statcheck` validates that four counted strings fit exactly within the supplied stat buffer.
- `convM2D` reads fixed stat fields and the four strings; if `strs` is provided, copies strings there and points `Dir` fields into it, otherwise assigns a static empty string.

Notable behavior:
- Bounds checks string count/data extents against the end of the supplied buffer.
- Ignores the leading size field while parsing.
