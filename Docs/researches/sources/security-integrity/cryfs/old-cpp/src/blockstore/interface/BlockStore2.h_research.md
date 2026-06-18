# sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore2.h

## Purpose
Defines a block-store abstraction for creating, loading, storing, and removing block payloads by `BlockId`; the default `create` loop repeatedly allocates random IDs until `tryCreate` succeeds. This specific file has 53 source lines under `sources/security-integrity/cryfs/old-cpp/src/blockstore/interface` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `BlockStore2`. Macros/constants: `MESSMER_BLOCKSTORE_INTERFACE_BLOCKSTORE2_H_`. Important declarations or call sites include `virtual ~BlockStore2() {}`; `virtual BlockId createBlockId() const {`; `return BlockId::Random();`; `virtual bool tryCreate(const BlockId &blockId, const cpputils::Data &data) = 0;`; `virtual bool remove(const BlockId &blockId) = 0;`; `virtual boost::optional<cpputils::Data> load(const BlockId &blockId) const = 0;`; `virtual void store(const BlockId &blockId, const cpputils::Data &data) = 0;`; `BlockId create(const cpputils::Data& data) {`; `while (true) {`; `BlockId blockId = createBlockId();`. CMake commands used here include `while`, `if`. Primary includes/dependencies visible in the file include `Block.h`, `string`, `boost/optional.hpp`, `cpp-utils/pointer/unique_ref.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/Random.h`.

## Control Flow
The important flow is `create(data)`: generate an ID via `createBlockId`, call virtual `tryCreate`, and retry until no collision occurs. Implementations provide the persistence behavior behind the virtual calls.

## State and Persistence Behavior
The interface itself stores no state; concrete block stores decide whether data is persisted, cached, or encrypted. The `create` retry loop relies on random `BlockId` uniqueness but does not record attempts.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Block.h`, `string`, `boost/optional.hpp`, `cpp-utils/pointer/unique_ref.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/Random.h`.

## Risks and Edge Cases
A broken `tryCreate` implementation could make `create` spin forever. Collision handling and atomicity are delegated to implementations, so tests must cover duplicate IDs and partial writes.

## Test Signals
Exercise `tryCreate` collision, load/store/remove round trips, optional miss behavior, and ID uniqueness under repeated creation.

## File-Specific Notes
- `BlockStore2` exposes `tryCreate`, `remove`, `load`, and `store`; `create` is an inline convenience API that retries on random block-ID collisions.
