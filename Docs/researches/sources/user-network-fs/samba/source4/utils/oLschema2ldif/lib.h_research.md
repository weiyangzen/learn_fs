<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.h -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.h

## Purpose

This header exposes the minimal public interface for the `oLschema2ldif` converter library.

## Important APIs, Types, and Functions

- `struct schema_conv` reports `count` and `failures` from a conversion run.
- `struct conv_options` carries the LDB context, base DN, input stream, and output stream.
- `process_file()` is the single exported conversion function.

## Control Flow

Consumers fill `conv_options`, call `process_file()`, and inspect the returned counters. The header itself contains no logic.

## State and Persistence Behavior

The caller owns the LDB context, base DN, and streams. Conversion state is owned by `process_file()` and its caller-provided talloc context.

## Dependencies and Integration Points

The header includes Samba `includes.h`, `ldb.h`, and DSDB/SAMDB headers because the converter uses LDB and schema syntax APIs. It is included by both `main.c` and `test.c`.

## Risks and Edge Cases

The API assumes valid, open `FILE *` handles and a valid `ldb_dn`. It exposes only aggregate counts, not structured parse errors or per-entry diagnostics.

## Test Signals

Build success and clean inclusion by the command-line tool and cmocka tests are the primary signals. Runtime callers should see accurate `count` and `failures` fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.h -->
