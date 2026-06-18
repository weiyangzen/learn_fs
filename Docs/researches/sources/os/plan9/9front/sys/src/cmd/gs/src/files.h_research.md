# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/files.h

## Scope

Interpreter support declarations and macros for PostScript file objects.

## Key Behavior

- Defines file refs as refs whose `value.pfile` points to a Ghostscript `stream`.
- Validates file refs by comparing ref size against stream `read_id` / `write_id`.
- Provides macros for checking read/write file access and switching bidirectional streams between read and write modes.
- Declares accessors for stdin/stdout/stderr refs and lazy stream retrieval.
- Declares file opening, closing, stream allocation, filter opening, string reading, line reading, and line-edit helpers.

## Dependencies

Requires `stream.h`-style stream definitions, interpreter context refs, Ghostscript memory types, IODevice types, and zfile/zfileio/zfilter/ziodev implementations.

## Risks And Invariants

- File validity depends on stream generation IDs; reusing streams after close must update IDs.
- Bidirectional streams may switch mode when a read/write ID check fails.
- `file_is_invalid` is required instead of negating `file_is_valid` due to historical compiler behavior.
