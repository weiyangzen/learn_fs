# sources/storage-engines/wiredtiger/test/simulator/CMakeLists.txt

Purpose: top-level CMake entry for simulator tests.

Important APIs and control flow: contains a single `add_subdirectory(timestamp)` call that delegates all simulator build work to the timestamp subtree.

State and persistence behavior: no runtime state. It contributes CMake graph structure only.

Dependencies and integration points: integrated by the parent test CMake tree and depends on the `timestamp` directory existing.

Risks: currently only timestamp simulator is represented; adding more simulator domains requires explicit subdirectories here.

Test signals: configure should descend into `test/simulator/timestamp` and create its library/executable targets.
