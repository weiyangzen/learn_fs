# sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/FileConverter.h

## Purpose

`FileConverter.h` defines the CLI option identifiers and `CSimpleOpt` option table for the fdbbackup file-converter tool. The converter appears to read backup files or containers, filter versions/key prefixes, validate filters, optionally save output, and handle encryption/blobstore transport.

## Important APIs, Types, and Functions

The header exposes namespace `file_converter`, an anonymous enum of option IDs, and the global `CSimpleOpt::SOption gConverterOptions[]`. Supported options include container URL (`-r`, `--container`), file type (`-t`, `--file-type`), version bounds (`--begin`, `--end`), input file (`-i`, `--input`), blob credentials, trace settings, list-only, filter validation, key prefix and hex prefix, proxy, begin/end version filters, knobs, save mode, and encryption key file. It also embeds `TLS_OPTION_FLAGS`, making TLS configuration available to the converter.

## Control Flow

There is no executable logic in this header, but the option table controls downstream converter parse flow. `SO_REQ_SEP` options require a separate argument; `SO_NONE` options are flags; `--knob-` is a prefix option. `SO_END_OF_OPTIONS` terminates the table.

## State and Persistence Behavior

No state is directly stored by the header. Runtime converter behavior can read containers, local input files, credentials, and encryption keys; `--save` suggests it may write converted files. Trace options affect log output, and knob options alter client/runtime behavior.

## Dependencies and Integration Points

The header depends on `<cinttypes>`, `SimpleOpt/SimpleOpt.h`, and `flow/TLSConfig.h`. It shares CLI conventions with `backup.cpp`: blob credentials, TLS flags, trace options, proxy, knobs, encryption key file, and version-oriented filtering. Because the option array is defined in the header rather than declared `extern`, inclusion from multiple translation units would risk duplicate definitions unless intentionally included once.

## Risks and Edge Cases

The enum values are positional and coupled to the option table; adding new options must preserve uniqueness. Defining `gConverterOptions` in a header is a linkage hazard. Prefix filtering has both raw and hex forms, so call sites must reject ambiguous combinations if that matters. Since TLS and blob credentials are available at this layer, converter tests need to cover both local and blobstore inputs.

## Test Signals

No tests in this subset directly invoke the file converter, but the shared backup tests cover adjacent option families: blob credentials, TLS-related S3 setup, encryption key files, proxy avoidance, and versioned backup container handling.
