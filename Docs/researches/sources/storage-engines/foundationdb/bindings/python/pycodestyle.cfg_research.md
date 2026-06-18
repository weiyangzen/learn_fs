# sources/storage-engines/foundationdb/bindings/python/pycodestyle.cfg

Purpose: This configuration defines local pycodestyle behavior for the Python FoundationDB binding.

Important APIs and types: It is a `[pycodestyle]` config file with `max-line-length = 150`, excludes generated `fdboptions.py`, and ignores selected E/W rules including comment style, import position, comparisons to `None`/booleans/types, bare except, and line-break operator variants.

Control flow: There is no runtime control flow. Tooling reads this file when pycodestyle runs in the bindings tree.

State and persistence behavior: It does not affect runtime state or database persistence. It affects developer feedback and CI lint acceptance.

Dependencies and integration points: It integrates with Python style tooling and with generated option files produced elsewhere in the build.

Risks: Several ignores permit legacy idioms that modern linters would flag. Excluding `fdboptions.py` is intentional because it is generated, but it means generated API surface style is not validated here.

Test signals: The signal is lint/tool success under this configuration, not unit-test behavior.
