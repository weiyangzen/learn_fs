# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.cpp

Purpose: Translation unit for the templated `CacheEntry` wrapper.

Important APIs and types: It includes `CacheEntry.h`; implementation lives in the header because `CacheEntry` is templated.

Control flow: No runtime control flow is present in this file.

State and persistence behavior: No state is defined here. Entry timestamp/value state is described in `CacheEntry.h`.

Dependencies and integration points: Included in the blockstore target source list for build/IDE visibility.

Risks: Behavioral risks are in the header; this file is effectively a placeholder.

Test signals: Tests instantiate `CacheEntry` indirectly through `Cache`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.cpp` completely for this pass (1 lines, 24 bytes).
