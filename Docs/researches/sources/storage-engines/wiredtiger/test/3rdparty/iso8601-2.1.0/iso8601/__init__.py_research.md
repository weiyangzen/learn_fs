<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/__init__.py

Purpose: Package facade for the vendored `iso8601` parser.

Important APIs/functions: Re-exports `UTC`, `FixedOffset`, `ParseError`, `is_iso8601`, and `parse_date` from `.iso8601`, and declares the same public names in `__all__`.

Control flow: Import-only module; importing `iso8601` imports the implementation module and binds public symbols.

State and persistence behavior: No durable state. It compiles/imports the regex in the implementation module as a side effect.

Dependencies and integration points: Gives consumers a stable package-level API, used by tests and any WiredTiger Python tooling that imports vendored `iso8601`.

Risks: `__all__` omits internal helpers such as `parse_timezone` and `ISO8601_REGEX`, though direct submodule imports can still access them. Import failure in implementation prevents package import.

Test signals: Tests import `.iso8601` directly for internals and package facade behavior can be covered by importing `from iso8601 import parse_date`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/__init__.py -->
