<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_options.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_options.h

## Purpose
`json_spirit_writer_options.h` declares the bit flags controlling json_spirit JSON output formatting and character escaping.

## Important APIs, Types, and Functions
The file defines `json_spirit::Output_options` values `none`, `pretty_print`, `raw_utf8`, `remove_trailing_zeros`, `single_line_arrays`, and `always_escape_nonascii`.

## Control Flow
Writer code treats these enum values as bit flags. Pretty and single-line array modes influence whitespace and newlines, UTF-8 and non-ASCII flags influence string escaping, and `remove_trailing_zeros` influences default double precision.

## State and Persistence Behavior
The file contains only constants and has no runtime state. Its effects are visible in serialized JSON output.

## Dependencies and Integration Points
It has no external include dependencies and is consumed by `json_spirit_writer_template.h`.

## Risks and Edge Cases
`single_line_arrays` is marked as no longer used but still affects writer behavior for compatibility. `raw_utf8` intentionally permits non-standard raw non-printable output. Since this is a plain enum, callers can combine invalid or unknown bits without type protection.

## Test Signals
Writer tests should cover each flag and combinations, especially pretty printing, single-line arrays, raw UTF-8, forced escaping, and double precision behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_options.h -->
