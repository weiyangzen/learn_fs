<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/update-proto.pl -->
# sources/user-network-fs/samba/source4/script/update-proto.pl

## Purpose

`update-proto.pl` updates an existing C prototype header while trying to preserve surrounding formatting and comments.

## Important APIs, Types, and Functions

Options are `--help` and `--verbose`. `%new_protos` stores prototypes parsed from source files. Important functions are `count()`, `process_file()`, and `insert_new_protos()`.

## Control Flow

The script reads the target header and optional C files. It parses non-static function definitions into `%new_protos`. While streaming the header, it recognizes `/* The following definitions come from FILE */` markers to refresh source-derived prototypes, inserts new prototypes above the configured marker, updates changed prototypes, removes deleted prototypes, and reports counts on stderr.

## State and Persistence Behavior

It writes the updated header to stdout rather than modifying the file directly. New prototype state is in memory.

## Dependencies and Integration Points

It depends on Perl and is part of older Samba prototype maintenance workflows, complementary to generated autoproto headers.

## Risks and Edge Cases

Regex parsing cannot handle all C syntax, especially macros and function-pointer returns. The header must use expected comments for best results. Callers must redirect stdout safely to avoid losing headers on failure.

## Test Signals

Tests should cover added, modified, deleted, and kept prototypes; marker-driven source parsing; duplicate prototypes; verbose output; and malformed source/header input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/update-proto.pl -->
