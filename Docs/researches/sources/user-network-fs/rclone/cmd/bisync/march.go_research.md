# sources/user-network-fs/rclone/cmd/bisync/march.go

Purpose: Builds current Path1 and Path2 listings by walking both filesystems with rclone's `march` engine and recording files, optional directories, hashes, modtimes, and alias relationships.

Important APIs/types/functions: `bisyncMarch` stores current `fileList`s, first errors, context, and locks for concurrent callbacks. `makeMarchListing` runs the two-sided march and saves `-new` listings. Callback methods `SrcOnly`, `DstOnly`, and `Match` implement `march.March` behavior. `parse`, `ForObject`, and `ForDir` add entries. `findCheckFiles` runs a filtered march for check-access during resync. `ID` extracts object IDs when supported, though current listing code leaves IDs blank.

Control flow: `makeMarchListing` stores the context, initializes listing hash types, configures `march.March` with Path2 as destination and Path1 as source, and runs it. Callbacks parse source-only, destination-only, and matched entries, with matches also adding aliases for normalized/case-varied names. Object callbacks register checking transfers, compute configured hashes and optional download hashes, record first hash error, capture modtime if enabled, and append to the appropriate listing under lock. Successful marches save both new listings.

State and persistence behavior: Writes `b.newListing1` and `b.newListing2`, which later become durable current listings or feed delta detection. Mutates `b.march.ls1`, `b.march.ls2`, `b.aliases`, and `b.march.firstErr`. Directory entries are only persisted when `CreateEmptySrcDirs` is enabled.

Dependencies and integration points: Depends on rclone `fs/march`, `fs/accounting`, filters, hash support, and listing serialization. Called by normal `runLocked`; `findCheckFiles` is used by resync check-access.

Risks: March callbacks may be concurrent, so alias/list/error locks are required. Hash errors are captured as firstErr and can abort later. Download-hash during listing can be expensive. Directory support is conditional and can alter downstream delta/listing behavior.

Test signals: Normal and resync tests exercise listing generation. Empty-dir, normalization, compare-all, download-hash, and check-access scenarios are especially relevant. Focused tests would simulate hash errors, aliases from case/unicode normalization, and directory inclusion toggles.
