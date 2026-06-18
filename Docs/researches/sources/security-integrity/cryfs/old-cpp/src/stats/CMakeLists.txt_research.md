# sources/security-integrity/cryfs/old-cpp/src/stats/CMakeLists.txt

Purpose: builds the `cryfs-stats` executable.

Important APIs/types/functions: target `stats`, sources `main.cpp` and `traversal.cpp`, link libraries `cryfs`, `cpp-utils`, `gitversion`, and output name `cryfs-stats`.

Control flow: declares an executable, links dependencies, enables style warnings and C++14, and renames the generated binary.

State and persistence behavior: no runtime state in the build file; it wires the stats tool into the build.

Dependencies and integration points: depends on the main CryFS library plus utility and version targets.

Risks and test signals: no tests are registered here; correctness is inferred from executable build and any manual/integration use of `cryfs-stats`.
