<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.h -->
# sources/sync-backup/unison/src/uimac/ReconItem.h

Source read: complete file, 80 lines, 1934 bytes, sha256 `91694cf98bce0176`.

Purpose: Declares the model hierarchy for reconciliation rows displayed by the Mac UI: base `ReconItem`, OCaml-backed `LeafReconItem`, and aggregating `ParentReconItem`.

Important APIs/types/functions: Base methods expose path/full path, replica change summaries, direction, icons, file counts/sizes, progress, details, conflict/default state, action/ignore commands, diff behavior, sort keys, and tree navigation. `LeafReconItem` initializes from an OCaml recon item and list index. `ParentReconItem` adds children, sorting, and conflict aggregation.

Implementation inventory: discovered Objective-C/C callback methods include `selected, setSelected, path, fullPath, left, right, direction, fileIcon, fileCount, fileSize, fileSizeString, bytesTransferred, bytesTransferredString, setDirection, doAction, doIgnore, progress, progressString, resetProgress, details, updateDetails, isConflict, changedFromDefault, revertDirection, canDiff, showDiffs, leftSortKey, rightSortKey` and more.

Control flow: `MyController` builds leaves from OCaml data and inserts them into parent nodes for flat or nested table modes. Table delegates ask these objects for display values, sorting keys, and action handlers.

State and persistence behavior: Base state stores parent/path/fullPath, selection flag, cached direction image/sort key, cached size/progress values, and resolved flag. Leaves keep OCaml recon item handles and index; parents keep children and aggregate counts.

Dependencies and integration points: Depends on Cocoa and `OCamlValue` from the bridge; integrates tightly with `MyController` and `ReconTableView`.

Risks: The model mixes UI caches with OCaml-backed mutable synchronization state. Incorrect cache invalidation can show stale direction/progress/file size.

Test signals: Build nested and flat recon trees, sort by every column, execute every action/ignore command, and verify table values after OCaml progress updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.h -->
