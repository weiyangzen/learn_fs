# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/CMakeLists.txt

Purpose: CMake build definition for the `parallelaccessstore` static library.

Important APIs/types/functions: target `parallelaccessstore`, sources `ParallelAccessBaseStore.cpp` and `ParallelAccessStore.cpp`, `target_link_libraries(cpp-utils)`, Boost helper, style warnings, and C++14 activation.

Control flow: declares a static library from two translation units, though most implementation lives in headers due templates.

State and persistence behavior: no runtime state; build target exposes parallel access abstractions to block/blob store layers.

Dependencies and integration points: links `cpp-utils` and Boost support, and participates in the old C++ CryFS build graph.

Risks and test signals: source `.cpp` files only include headers, so build coverage mostly verifies template headers compile in at least one target but does not instantiate all combinations.
