# sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheck.go

Purpose: first-stage filter over Git object IDs using `git cat-file --batch-check`, passing only small blobs to pointer decoding while separately detecting large lockable blobs.

Important APIs/types/functions: `runCatFileBatchCheck`, `catFileBatchCheckScanner`, `LFSBlobOID`, `GitBlobOID`, `Scan`, `Err`, and `next`.

Control flow: a goroutine writes each upstream SHA to cat-file stdin, scans one response, sends small blob IDs to `smallRevCh`, checks lockable names for large blobs, waits on upstream, closes stdin, waits on cat-file, and closes channels. The parser expects `<hash> blob <size>`, ignores non-blobs/malformed sizes, and classifies size below cutoff as possible LFS pointer.

State/persistence behavior: read-only subprocess interaction with channels.

Dependencies/integration: used before `catFileBatch` in ref/index scanning to avoid reading large objects unnecessarily.

Risks/test signals: assumes one cat-file output line per input and does not handle process write errors directly. Tests cover malformed lines, capitalized type, invalid size, small blob, malformed extra size, and large blob classification.
