# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testresult/__init__.py

Purpose: public facade for testtools result classes and decorators.

Important APIs, types, and functions: `__all__` exposes stream, extended, decorator, routing, summary, queue, failfast, multi-result, text-result, and timestamping result classes. Imports all public names from `testtools.testresult.real`.

Control flow: import-time aggregation only; no behavior beyond loading `real.py` symbols into this package namespace.

State and persistence: module globals hold imported classes/functions. No persistence.

Dependencies and integration points: depends on `testtools.testresult.real`, which supplies the actual result implementations used by `TestCase`, `RunTest`, the runner, and stream adapters.

Risks and test signals: facade import fails if `real.py` or any of its dependencies are broken. Public API consistency depends on `__all__` matching actual imports. Test signals are import coverage and downstream use by `testtools.__init__`.
