# sources/sync-backup/git-lfs/lfs/gitscanner_pointerscanner_test.go

Purpose: tests `PointerScanner` over in-memory Git objects.

Important APIs/types/functions: `PointerScanner.Scan`, `Pointer`, `ContentsSha`, `git.NewObjectScannerFrom`, `gitobj.NewMemoryBackend`, `fakeObjectsWithRandoData`, and `writeFakeBuffer`.

Control flow: creates random non-pointer blobs and encoded pointer blobs, writes them to an in-memory object database, scans them sequentially, and asserts pointer detection only for actual pointer blobs. A separate large-blob test verifies no pointer is produced and `ContentsSha` equals the content hash.

State/persistence behavior: in-memory object database only.

Dependencies/integration: validates interaction between `PointerScanner`, `ObjectScanner`, pointer encoding/decoding, and blob size cutoff.

Risks/test signals: deterministic random source makes tests reproducible. It does not cover missing objects, object close errors, or malformed pointer errors.
