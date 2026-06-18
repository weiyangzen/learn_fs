# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_immutable.py

## Purpose
Tests immutable downloader behavior, a `ShareFinder` asynchronous edge case, degraded no-network-grid downloads, immutable filenode convenience APIs, and `LiteralFileNode` equality.

## APIs / Types / Functions
- `MockNode` and `MockShareHashTree` model downloader consumer behavior.
- `TestShareFinder.test_no_reneging_on_no_more_shares_ever` guards a race where no-more-shares must not be followed by another share.
- `Test.startup` configures a two-client, five-server grid, uploads `TEST_DATA`, and creates a reader filenode.
- Counter helpers inspect storage read/allocate/write counters.
- `LiteralFileNodeTests` validates URI-based equality.

## Control Flow
The synthetic share-finder test creates mocked servers returning shares asynchronously and fails if the consumer receives an inconsistent no-more-shares/further-share sequence. Grid tests upload immutable data, delete or corrupt shares, then download or expect `NotEnoughSharesError`. Additional tests call `download_to_data`, `download_best_version`, `get_best_readable_version`, and `get_size_of_best_version`.

## State And Persistence
No-network storage creates real share files and server stats. Tests mutate shares with `delete_shares_numbered` and `corrupt_shares_numbered`, tracking `self.uri` and `self.filenode`.

## Dependencies / Integration Points
Uses immutable upload `Data`, downloader `finder.ShareFinder`, URI verify caps, no-network server wrappers, corruption helpers, and storage stats.

## Risks And Test Signals
The file notes `TODO: delete this whole file`, so some coverage is legacy. Read-count assertions may be sensitive to downloader pipeline changes. Passing tests signal recoverability from degraded shares, quick failure with too few/corrupt shares, and stable literal-node equality.
