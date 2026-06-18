# sources/sync-backup/git-lfs/git/object_scanner.go

Purpose: object database scanner for loading arbitrary Git objects by OID, with blob contents and size exposed for pointer detection.

Important APIs/types/functions: `ObjectScanner`, `NewObjectScanner`, `NewObjectScannerFrom`, `Scan`, `Close`, `Contents`, `Sha1`, `Size`, `Type`, `Err`, `IsMissingObject`, and `missingErr`.

Control flow: `Scan` resets/close previous object, decodes the hex OID, loads it through `gitobj.ObjectDatabase`, maps no-such-object to `missingErr`, and exposes blob contents/size when the object is a blob. `Close` resets and closes the object database.

State/persistence behavior: read-only object access but owns closable object handles. Previous object resources are closed before each scan.

Dependencies/integration: used by LFS `PointerScanner` and tree scanning; depends on `GitCommonDir`, `ObjectDatabase`, and `gitobj`.

Risks/test signals: `mustDecode` ignores decode errors, so malformed OIDs may become invalid byte slices passed to `gitobj`. Accessors assume a successful scan set `s.object`. Missing object classification is available for callers.
