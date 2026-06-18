# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_const.py

Purpose: constant matchers that always succeed or always fail.

Important APIs, types, and functions: `Always()` returns `_Always`, whose `match()` returns `None`. `Never()` returns `_Never`, whose `match()` returns a `Mismatch` containing the inspected value.

Control flow: factory functions allocate new matcher objects. Matching does not inspect any external state.

State and persistence: no mutable state beyond object identity. No persistence.

Dependencies and integration points: depends on core `Mismatch`. Useful as defaults and placeholders in higher-order matchers such as warning message matchers.

Risks and test signals: intentionally trivial; string representations and guaranteed success/failure are the main test signals.
