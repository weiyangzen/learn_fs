# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/TwoLevelDataFixture.h

Purpose: recursive fixture helper for filling and verifying leaf data across a data-node tree, despite the historical "TwoLevel" name.

Important APIs/types/functions: `TwoLevelDataFixture`, `SizePolicy::{Random, Full, Unchanged}`, `FillInto`, `EXPECT_DATA_CORRECT`, `ForEachLeaf`, and `size`.

Control flow: recursively walks `DataNode` trees with dynamic casts. For each leaf in the selected range, it creates a `LeafDataFixture` using deterministic seed/leaf index and fills or checks content.

State and persistence behavior: loads child nodes from `DataNodeStore`, mutates leaf sizes/content during fill, and verifies persisted leaf bytes during checks.

Dependencies and integration points: uses `DataNodeStore`, `DataInnerNode`, `DataLeafNode`, `LeafDataFixture`, `cpputils::ASSERT`, and dynamic casts.

Risks and test signals: recursion supports more than two levels, but no cycle protection exists. `SizePolicy::Random` uses modular arithmetic to avoid negative sizes; incorrect layout limits would affect fixture generation.
