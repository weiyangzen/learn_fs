<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/sparsewrite.go -->
# sources/sync-backup/restic/internal/restorer/sparsewrite.go

## Purpose
Overrides `partialFile.WriteAt` to make sparse restore writes skip leading zero data when the file is marked sparse.

## Important APIs and Control Flow
`partialFile.WriteAt` delegates directly to the underlying file for non-sparse files. For sparse files, it computes the longest all-zero prefix with `restic.ZeroPrefixLen`, advances the write offset by that prefix, and writes only the remaining suffix. If the whole buffer is zero, it returns the original length without issuing a write because prior truncation or earlier writes establish the logical zeros.

## State, Persistence, Dependencies, and Integration
Persistent state is the target file's sparse allocation and content. It integrates with `filesWriter.writeToFile`, `truncateSparse`, and the restic zero-prefix helper.

## Risks and Test Signals
Risks are returning a successful byte count without actual writes when file sizing was not prepared correctly, and only skipping leading zeros rather than interior zero ranges. Sparse restore tests validate content and block-count behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/sparsewrite.go -->
