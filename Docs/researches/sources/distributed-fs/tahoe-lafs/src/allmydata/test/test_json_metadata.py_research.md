# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_json_metadata.py

## Purpose
Tests `allmydata.web.common.get_filenode_metadata` size-field behavior for immutable, SDMF, and MDMF filenodes.

## APIs / Types / Functions
- `MockFileNode` implements `get_size`, `is_mutable`, and `get_version`.
- `CommonFixture` defines shared tests for size `0`, size `1000`, and size `None`.
- Concrete classes set `mutable_version` to immutable (`None`), `SDMF_VERSION`, or `MDMF_VERSION`.

## Control Flow
Each concrete test class constructs a mock filenode, calls `get_filenode_metadata`, and asserts numeric sizes are included while `None` omits the `size` key.

## State And Persistence
All state is in-memory mock object data. No files or network resources are used.

## Dependencies / Integration Points
Protects the Tahoe web metadata response used by JSON clients and directory/file status consumers.

## Risks And Test Signals
Only size behavior is covered, not all metadata fields. Passing tests show `0` is treated as real data, large sizes are preserved, and unknown sizes are omitted across immutable and mutable versions.
