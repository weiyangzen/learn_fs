# sources/storage-engines/wiredtiger/tools/wt_to_mdb_bson.py Research

## Purpose

`wt_to_mdb_bson.py` converts MongoDB BSON values embedded in WiredTiger utility output into human-readable Python pretty output or Canonical Extended JSON. It supports output from `wt dump -x`, `wt verify -d dump_pages`, and `wt printlog -x -u`, either by reading stdin or by executing a provided `wt` binary.

## Important APIs, Types, and Functions

`Mode` distinguishes `DUMP`, `VERIFY`, and `PRINTLOG`. `print_bson()` formats decoded BSON as canonical JSON via `bson.json_util.dumps(..., CANONICAL_JSON_OPTIONS)` or as indented `pprint.pformat`. `convert_byte()` converts the escaped byte representation emitted by verify output into bytes suitable for BSON decoding. `wt_verify_to_bson()`, `wt_printlog_to_bson()`, and `wt_dump_to_bson()` implement the three conversion modes. `find_data_section()` and `decode_data_section()` locate and decode `wt dump` data pairs. `execute_wt()` builds subprocess argument lists for the supported `wt` invocations. `main()` owns argparse, mode mapping, stdin/subprocess selection, and dispatch.

## Control Flow

The CLI requires `-m/--mode` and optionally accepts `-j/--json`, `-f/--wt-path`, and an optional URI. If either URI or wt path is supplied, both are required by validation, although `printlog` later ignores the URI by passing `None` internally. Without `-f`, all input is read from stdin as lines. Dump mode searches for a `Data` marker and then decodes alternating key/value hex lines. Verify mode echoes every original line and appends decoded BSON under matching `V {...}` records. Printlog mode searches each line for `value-hex`, decodes it when possible, and otherwise preserves the original value-hex line.

## State and Persistence Behavior

The script does not mutate database contents. It may spawn the `wt` executable and read all subprocess stdout into memory. It writes converted content to stdout only. No temporary files are created.

## Dependencies and Integration Points

It depends on PyMongo's `bson` package, `bson.json_util`, Python `codecs`, `subprocess`, `argparse`, and regexes that match current `wt` output formats. It integrates with WiredTiger command output and MongoDB data files, especially `_mdb_catalog.wt` and value records that are BSON documents.

## Risks and Edge Cases

`decode_data_section()` assumes an even number of lines after `Data`; malformed dump output can index past the end. `convert_byte()` reads `inp[idx+1]` after a backslash without checking bounds, so truncated escapes can fail. Printlog decoding catches all exceptions and silently falls back to hex, which is robust but can hide format drift. Regexes are narrow and may fail if `wt` output spacing changes. The `printlog` path requires a URI whenever `-f` is used even though it does not use one, which is a CLI ergonomics issue. The subprocess call for printlog hard-codes `log=(compressor=snappy,path=journal/)`, coupling the tool to MongoDB journal layout and snappy availability.

## Test Signals

Fixtures should cover all three modes using captured `wt` output, both pretty and JSON output, invalid BSON fallback in printlog, verify escaped bytes with single and double backslashes, dumps without `Data`, odd dump line counts, and subprocess argument construction.
