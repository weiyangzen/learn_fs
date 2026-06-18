# sources/user-network-fs/impacket/examples/registry-read.py

## Purpose

`registry-read.py` is an offline Windows registry hive reader. It opens a local hive through Impacket `winregistry`, then enumerates keys, enumerates values, reads a value, reads class metadata, or walks a subtree.

## Important APIs, Types, and Functions

`bootKey()` demonstrates SYSTEM boot key reconstruction from `ControlSet001\Control\Lsa\JD`, `Skew1`, `GBG`, and `Data` class data, although it is not exposed through the CLI. `getClass()`, `getValue()`, `enumValues()`, `enumKey()`, and `walk()` are thin wrappers around parser methods. `main()` owns argument parsing, logger setup, parser creation through `winregistry.get_registry_parser()`, action dispatch, and `reg.close()`.

## Control Flow

The script requires a hive path and one subcommand. After parsing and logger setup, it opens the hive parser and dispatches by uppercase action. `enum_key` finds a key and prints child keys, recursing when requested. `enum_values` lists value names and uses `printValue()` for each. `get_value` and `get_class` print one value/class payload. `walk` delegates traversal to the parser. The parser is closed at the end of normal execution.

## State and Persistence Behavior

The script is read-only for the input hive. It prints decoded data to stdout and does not write output files. It holds hive parser state until `close()`.

## Dependencies and Integration Points

It depends on `impacket.winregistry`, `ntpath` for key/value path splitting, `hexlify`/`unhexlify` for boot key demonstration, and the Impacket example logger. It integrates with offline registry hive files, not the remote registry protocol.

## Risks and Edge Cases

The CLI does not expose `bootKey()`, and that function mixes byte-oriented `unhexlify()` output with a string accumulator, which is fragile under Python 3 if called. Missing keys simply return without explicit status. `enumValues()` decodes value names as UTF-8, which can fail for unusual names. The parser is not closed if an exception occurs before the final close.

## Test Signals

Tests should use small fixture hives to verify key enumeration, recursive traversal, value rendering, class rendering, missing-key behavior, and binary value formatting. A direct test of `bootKey()` should catch Python 3 byte/string compatibility.
