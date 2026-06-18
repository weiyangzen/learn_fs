# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.cpp

Purpose: Translation unit for `MockBlockStore`.

Important APIs and types: It includes `MockBlockStore.h`; implementation is inline in the header.

Control flow: No runtime control flow is present here.

State and persistence behavior: No state is defined here. Counter and base-store behavior live in the header.

Dependencies and integration points: Included in the blockstore target source list.

Risks: Behavioral risks are in `MockBlockStore.h`.

Test signals: Access-counting tests instantiate the header-defined class.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.cpp` completely for this pass (1 lines, 28 bytes).
