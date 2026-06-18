# sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/NodeTest.cpp

Purpose: This file tests common fspp node interface behavior such as stat metadata, names, and type-specific expectations shared by files, directories, and devices.

Important APIs/types/functions: Includes: fspp/fs_interface/Node.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none.

Control flow: Google Test fixtures instantiate interface implementations or mocks, call the interface methods under test, and assert returned values, propagated exceptions, or metadata fields.

State and persistence behavior: These tests are primarily in-memory interface/fixture checks. Any filesystem-like state is represented by mocks or lightweight test objects rather than durable files.

Dependencies and integration points: These interface tests sit below the FUSE adapter tests and above concrete filesystem implementations such as CryFS, keeping the fspp abstraction contract explicit.

Risks: Interface drift can break both FUSE adapters and real filesystem backends even if individual implementations still compile.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
