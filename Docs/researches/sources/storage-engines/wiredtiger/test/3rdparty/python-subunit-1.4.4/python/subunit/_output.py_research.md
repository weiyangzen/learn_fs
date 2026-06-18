# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_output.py

## Purpose

`_output.py` implements the `subunit-output` command helper. It generates subunit v2 `StreamResult` packets from CLI status options, tags, timestamps, and optional file attachments.

## Important APIs, Types, and Functions

`output_main()` parses command-line arguments, wraps stdout with `StreamResultToBytes`, and calls `generate_stream_results`. `parse_arguments()` creates option groups for status commands (`--exists`, `--fail`, `--skip`, `--success`, `--uxsuccess`, `--xfail`, `--inprogress`) and file options (`--attach-file`, `--file-name`, `--mimetype`, `--tag`). `set_status_cb()` enforces a single status command and extracts the following `TEST_ID`. `generate_stream_results()` emits `startTestRun`, one or more `status` calls, and `stopTestRun`. `_CHUNK_SIZE` is 3.5 MiB.

## Control Flow

Argument parsing validates that `--mimetype` and `--file-name` appear only with `--attach-file`. Attachments are opened in binary mode; `-` is converted to binary stdin and defaults `file_name` to `stdin`. Generation sends timestamp and tags on the first packet only. For final statuses, `test_status` is delayed until the last packet when attachments are chunked; for `inprogress`, status is emitted on the first packet. EOF is set when the next read is empty.

## State and Persistence Behavior

State is local to the parsed options and attachment reader. The command writes a binary subunit stream to stdout and opens but does not explicitly close attachment files in this module. No files are persisted except what callers redirect.

## Dependencies and Integration Points

It depends on `optparse`, `iso8601.UTC`, `subunit.make_stream_binary`, and `subunit.v2.StreamResultToBytes`. It is exposed by `filter_scripts/subunit_output.py` and likely by packaging entry points.

## Risks and Test Signals

Risks include option parser compatibility, binary stdin handling, and multi-packet attachment metadata duplication. `test_output_filter.py` is extensive: it verifies all status commands parse, required test ids, invalid option combinations, file chunking, binary and empty files, stdin attachments, single-use tags/timestamps/mimetypes, and final-status placement.
