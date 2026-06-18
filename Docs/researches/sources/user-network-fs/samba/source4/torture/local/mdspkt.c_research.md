# sources/user-network-fs/samba/source4/torture/local/mdspkt.c

## Purpose
This file tests mdssvc packet unmarshalling for a fixture containing an empty CNID file-metadata structure.

## Important APIs, types, and functions
The fixture bytes are `mdspkt_empty_cnid_fm`, with expected textual dump `mdspkt_empty_cnid_fm_dump`. `test_mdspkt_empty_cnid_fm()` uses `dalloc_new`, `sl_unpack`, `dalloc_get`, `dalloc_size`, and `dalloc_dump`. `torture_local_mdspkt()` registers the test.

## Control flow
The test unpacks the fixture into a DALLOC tree, retrieves the `sl_cnids_t` node, asserts the CNID array has size zero, dumps the tree, and compares the dump exactly against the expected string.

## State and persistence behavior
No persistent state is written. All state is an in-memory DALLOC tree allocated under the torture context and freed at the end.

## Dependencies and integration points
It depends on `mdssvc/marshalling.h`, DALLOC helpers, Samba data-blob utilities, and the local smbtorture suite.

## Risks and edge cases
The exact dump string makes the test sensitive to formatting changes in `dalloc_dump`, not just decoding behavior. The fixture specifically covers empty CNIDs, so non-empty packet cases are not exercised here.

## Test signals
Passing confirms the mdssvc marshaller can parse the fixture, represent empty CNID arrays correctly, and emit the expected diagnostic tree.
