# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/details.py

## Purpose

`details.py` parses v1 subunit outcome details, either simple bracketed traceback/message blocks or multipart MIME-like detail blocks with chunked payloads.

## Important APIs, Types, and Functions

`DetailsParser` is an empty base marker. `SimpleDetailsParser(state)` accumulates lines until `]\n`, unescapes lines beginning ` ]`, and returns either a `traceback`, `reason`, or `message` `testtools.content.Content` object. `MultipartDetailsParser(state)` parses `Content-Type`, part name, chunked body, and returns a dict of named `Content` objects.

## Control Flow

Simple parsing appends lines to `_message` until the end marker asks the parent state to end details. Multipart parsing uses a three-function state machine: `_look_for_content`, `_get_name`, and `_feed_chunks`. Once a chunked parser returns residue, the body is stored as a `Content` object and the parser returns to looking for the next content header.

## State and Persistence Behavior

The parsers keep accumulated bytes in memory. `MultipartDetailsParser` stores part bodies in `BytesIO` before creating content lambdas that return the captured bytes. There is no filesystem persistence.

## Dependencies and Integration Points

The module depends on `testtools.content`, `testtools.content_type`, and `subunit.chunked`. It is called by `_ReadingDetails` states in `subunit.__init__.py`.

## Risks and Test Signals

Multipart parsing has intentionally minimal error handling: malformed `Content-Type` raises `ValueError`, but the TODO notes broader error handling is absent. Large attachments are fully buffered. `test_details.py` verifies simple message accumulation, escaped bracket handling, content type/name mapping for traceback/skip/success, and multipart chunk body reconstruction.
