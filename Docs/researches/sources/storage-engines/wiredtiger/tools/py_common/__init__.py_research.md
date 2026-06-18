# sources/storage-engines/wiredtiger/tools/py_common/__init__.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/__init__.py -->
## sources/storage-engines/wiredtiger/tools/py_common/__init__.py

### Purpose
`__init__.py` marks `py_common` as a Python package for shared WiredTiger tool helpers.

### Important APIs, Types, and Functions
The file exposes no package-level imports or functions; it only contains licensing text.

### Control Flow
There is no runtime control flow on import beyond executing the module body.

### State and Persistence
No state is stored or persisted.

### Dependencies and Integration Points
It enables imports such as `from py_common import binary_data` in decode tools including `btree_format.py`.

### Risks and Test Signals
Because it does not re-export modules, callers must import submodules explicitly. A simple import test from the tools root verifies package discoverability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/__init__.py -->
