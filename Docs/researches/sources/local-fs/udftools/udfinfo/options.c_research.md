# File Research: sources/local-fs/udftools/udfinfo/options.c

## Role

Command-line parser for `udfinfo`.

## Supported Options

- `--help` / `-h`
- `--blocksize` / `-b`
- `--startblock`
- `--lastblock`
- `--vatblock`
- `--locale`
- `--u8`
- `--u16`
- `--utf8`

## Behavior

- Validates block size as power of two from 512 through 32768.
- Stores optional start/last/VAT block hints in `struct udf_disc`.
- Updates charset flags used for string decoding.
- Requires exactly one device argument.

## Dependencies

- `libudffs.h` for numeric parsing and flags.
- `options.h` token definitions.

## Research Notes

Unlike mkudffs/udflabel charset parsing, this parser does not enforce charset options being first because it does not encode user-provided identifier strings, only decodes output.
