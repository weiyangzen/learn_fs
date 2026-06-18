# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/comments.h

Definitions for Adobe Document Structuring Convention comments.

Key responsibilities:
- Defines PostScript document classification strings.
- Defines header, body, page-level, resource, trailer, continuation, and non-standard comment constants.
- Defines `NONE`, `WARNING`, and `FATAL` severity constants used by some translators.

Notable details:
- Includes historical typos preserved in constants such as `DOCUMENTPRINTERREQUIRED`, `BEGINPAPERSIZE`, and `PAPERFORM`.
