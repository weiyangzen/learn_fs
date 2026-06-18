# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/LeafDataFixture.h

Purpose: helper for filling a data leaf with deterministic fixture bytes and later verifying those bytes.

Important APIs/types/functions: `LeafDataFixture`, constructor `(size, iv)`, `FillInto`, `EXPECT_DATA_CORRECT`, and private `loadData`.

Control flow: constructor generates data through `DataFixture`. `FillInto` resizes and writes a leaf. Verification reads the leaf into a buffer and compares full or prefix bytes.

State and persistence behavior: mutates `DataLeafNode` size and content. Data is stored in `_data` for expected comparison.

Dependencies and integration points: uses GoogleTest assertions, `cpputils::DataFixture`, `DataLeafNode::resize`, `write`, and `read`.

Risks and test signals: useful for content preservation checks. Optional prefix verification only asserts at least the requested bytes exist and does not verify bytes beyond the prefix.
