<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/mkproto.pl -->
# sources/user-network-fs/samba/source4/script/mkproto.pl

## Purpose

`mkproto.pl` generates C prototype headers from source files, splitting public `_PUBLIC_` functions from private prototypes when requested.

## Important APIs, Types, and Functions

Options include `--public`, `--private`, `--all`, `--define`, `--public-define`, `--private-define`, `--srcdir`, and `--builddir`. Key functions are `normalize_define()`, `file_load()`, `print_header()`, `print_footer()`, and `process_file()`. Output buffers are appended through `public()` and `private()`.

## Control Flow

The script parses options, derives include guard names, chooses whether public/private output share the same buffer, writes header prelude macros, processes each input C file, and emits detected function signatures. `process_file()` prefers builddir files, falls back to srcdir, captures Doxygen comments, skips indented lines, declarations, macros, and `main`, and reads multiline prototypes until a closing parenthesis.

## State and Persistence Behavior

It writes generated header files, creating parent directories with `mkpath`. If no output file is provided for one class, that class may be printed to stdout.

## Dependencies and Integration Points

It is used by Samba's build autoproto mechanism and depends on Perl `Getopt::Long`, `File::Basename`, and `File::Path`.

## Risks and Edge Cases

The parser is regex-based and can miss complex return types, function-pointer returns, macro-generated definitions, or unusual formatting. It writes generated files directly and can overwrite existing headers.

## Test Signals

Tests should cover public/private split, shared `--all` output, multiline prototypes, Doxygen comments, generated include guards, builddir fallback, and intentionally unsupported complex declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/mkproto.pl -->
