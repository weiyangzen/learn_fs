<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/auparse_python.c -->
# sources/security-integrity/audit-userspace/bindings/python/auparse_python.c

Purpose: CPython extension module `auparse` wrapping libauparse parser, search, feed, normalization, timestamp, and interpretation APIs.

Important APIs and types: defines `AuEvent` with lazy properties `sec`, `milli`, `serial`, `host`, string formatting, and rich timestamp comparison. Defines `AuParser` owning `auparse_state_t *`, initialized from logs, file, file array, buffer, buffer array, duplicated descriptor, duplicated file object, or feed source. Methods expose feed lifecycle, callbacks, escape and EOE timeout, reset, metrics, search expression/item/timestamp/regex APIs, event and record traversal, field traversal, field lookup, field values/types, interpretation, realpath, socket family/port/address, and normalization cursor helpers.

Control flow and state: object deallocation destroys the parser. Callback registration stores a `CallbackData` with Python function/user data and reconstructs Python calls from the C callback. Descriptor and file-object sources duplicate fd with `F_DUPFD_CLOEXEC` so parser destruction does not close caller-owned descriptors. Module init registers types, `NoParser`, source/search/stop/rule/type/escape constants.

Dependencies and integration: includes Python C API and `auparse.h`; links against libauparse/libaudit. Test coverage comes from `auparse_test.py` and the python3 Makefile no-undefined check.

Risks and test signals: risks include GIL assumptions in callbacks, reference ownership, stale Python-version conditionals, static buffers in event formatting, return-code mapping differences, and missing constants for newer C enum values. Descriptor/file-pointer tests directly validate ownership fixes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/auparse_python.c -->
