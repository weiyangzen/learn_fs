# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdscpars.c

Provides the C/PostScript bridge for Russell Lang's DSC parser.

`.initialize_dsc_parser` allocates a `dsc_data_t` wrapper, initializes a `CDSC` parser, installs an error handler that returns `CDSC_OK`, and stores the wrapper in a caller dictionary under `DSC_struct`.

`.parse_dsc_comments` accepts a dictionary and DSC comment string, truncates overly long comments to parser line length, appends a line terminator, skips data-block comments such as `%%BeginData:` and `%%BeginBinary:`, calls `dsc_scan_data()`, ignores parser errors, transfers recognized fields into the dictionary, and replaces the input string with a PostScript name identifying the comment type.

The command table maps parser codes to names such as `Header`, `Creator`, `CreationDate`, `Title`, `For`, `BoundingBox`, `Orientation`, `Page`, `Pages`, `PageOrientation`, `PageBoundingBox`, `ViewingOrientation`, and `EOF`.

Helper routines write integers, strings, bounding boxes, orientation enums, and viewing-orientation arrays through Ghostscript parameter-list APIs.

The finalizer frees the `CDSC` parser when the wrapper struct is collected.

Registered in `zdscpars_op_defs`.
