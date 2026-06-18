# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/__init__.py

Purpose: package marker for the legacy Python `headerlib` modules used by `syz-headerparser`.

Important APIs and flow: it contains only copyright/license comments and no runtime symbols.

State and persistence: none.

Dependencies and integration: allows `headerlib.container`, `headerlib.header_preprocessor`, and `headerlib.struct_walker` imports.

Risks: no functional risks beyond Python packaging expectations.

Test signals: import success when running `headerparser.py` is the practical signal.
