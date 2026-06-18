# File Research: sources/local-fs/udftools/cdrwtool/main.c

Main program for `cdrwtool`.

Startup flow:
- Initializes `struct cdrw_disc`, embedded `struct udf_disc`, and default UDF revision 1.50.
- Parses command-line options.
- Opens the CD/DVD device read-write nonblocking, falling back to read-only for `EROFS`.
- Installs a UDF writer callback that writes full 32-block packets through `write_blocks`.
- Validates media and drive locking.
- Reads buffer capacity and current write mode.
- Sets write speed.
- Dispatches exactly one requested operation.

Supported dispatch paths:
- Print write parameters and/or disc/track info.
- Set write mode.
- Close track or session.
- Quick setup.
- Blank disc.
- Format disc.
- Write a UDF session.
- Write an arbitrary file.
- Reserve a track.

`quick_setup` is the destructive high-level setup path:
- Prompts the user before proceeding.
- Fast blanks the disc.
- Reads disc/track geometry.
- Computes capacity from lead-out MSF data.
- Formats fixed-packet media or reserves a variable-packet track.
- Configures sparable partitioning and UDF allocation bitmap defaults.
- Builds VRS, anchors, partitions, VDS, and writes UDF structures to the disc.

`mkudf_session` is a narrower UDF-writing path using an explicit block count.

Notable details:
- `write_func` batches UDF descriptor/data writes into 32-block packets for packet media.
- The quick setup path sets the application identifier to `*Linux cdrwtool <version>`.
- Device lock cleanup is attempted before every return path after opening.
