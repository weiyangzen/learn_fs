# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.cpp

Purpose: Translation unit for the templated `QueueMap` addressable queue.

Important APIs and types: It includes `QueueMap.h`; all behavior is implemented in the header.

Control flow: No runtime control flow is present here.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Included in the blockstore target source list for build/IDE visibility.

Risks: Behavioral risks live in `QueueMap.h`.

Test signals: Tests should instantiate `QueueMap` indirectly through `Cache`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.cpp` completely for this pass (1 lines, 22 bytes).
