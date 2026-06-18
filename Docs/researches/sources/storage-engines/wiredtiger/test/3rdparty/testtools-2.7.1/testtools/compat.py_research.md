# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/compat.py

Purpose: compatibility helpers retained from testtools' Python 2/3 transition era, now used for byte/text handling, repr formatting, and stream encoding.

Important APIs, types, and functions: exports `_b`, `advance_iterator`, `reraise`, `unicode_output_stream`, `StringIO`, and `BytesIO`. `text_repr()` formats text or bytes, using triple quotes for multiline values. `unicode_output_stream()` wraps output streams so unencodable Unicode is replaced rather than raising. `_get_exception_encoding()` returns OS message encoding.

Control flow: `reraise()` raises an exception with its traceback. `_b()` encodes latin-1. `text_repr()` chooses single-line repr or multiline triple-quote formatting. `unicode_output_stream()` returns existing text/UTF streams or a codec writer/reconstructed stream with replacement error handling.

State and persistence: no persistent state. It reads locale/platform metadata and returns wrappers around caller-owned streams.

Dependencies and integration points: depends on `codecs`, `io`, `locale`, `os`, `sys`, and `unicodedata`. Used by content, matchers, test runner, and exception handling.

Risks and test signals: `_slow_escape()` can append bytes into a string list on some paths, reflecting legacy Python 2 assumptions. `unicode_output_stream()` relies on stream implementation details such as `.buffer`. Test signals are Unicode-rich mismatch output and runner output on non-UTF encodings.
