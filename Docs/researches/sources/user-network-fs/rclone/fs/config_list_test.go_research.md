<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list_test.go -->
# sources/user-network-fs/rclone/fs/config_list_test.go

## Purpose
Documents and verifies `SpaceSepList` and `CommaSepList` parsing/formatting.

## Important APIs, Types, And Control Flow
Examples show quoted spaces and doubled quotes for both separators. `TestSpaceSepListSet` table-drives empty input, backslashes, single quotes, double-quoted fields, multi-field input, and CSV parse errors.

## State And Persistence
Only local list values are mutated. No filesystem or global config state is touched.

## Dependencies And Integration Points
Uses `fmt` examples as documentation tests and testify `require` for assertions.

## Risks And Test Signals
The test is strong for current CSV behavior but mostly focused on space lists; comma list parsing is covered by examples rather than exhaustive invalid cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list_test.go -->
