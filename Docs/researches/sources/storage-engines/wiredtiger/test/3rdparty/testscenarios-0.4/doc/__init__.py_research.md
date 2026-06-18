# sources/storage-engines/wiredtiger/test/3rdparty/testscenarios-0.4/doc/__init__.py

Purpose: package marker for the `testscenarios` documentation examples. It contains only project copyright and dual-license text.

Important APIs, types, and functions: no executable APIs, imports, classes, functions, or constants are defined.

Control flow: importing `doc` executes only comments and produces an otherwise empty module namespace.

State and persistence: no runtime state, side effects, or persistent data.

Dependencies and integration points: included by `MANIFEST.in` through `doc/*.py`; it lets the example directory behave as a Python package if documentation tests import from it.

Risks and test signals: low behavioral risk because there is no code. Test signal is importability of the `doc` package and inclusion in source distributions.
