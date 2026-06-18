## sources/object-store/minio-mc/cmd/version-enable.go

Purpose: implements `mc version enable`, including optional excluded prefixes and folder-object exclusion for versioned buckets. Key surfaces are `versionEnableCmd`, `versionEnableFlags`, `versionEnableMessage`, `checkVersionEnableSyntax`, and `mainVersionEnable`.

Control flow requires exactly one `ALIAS/BUCKET`, splits `--excluded-prefixes` by comma, reads `--exclude-folders`, creates a client, and calls `client.SetVersion(ctx, "enable", excludedPrefixes, excludeFolders)`. State is remote bucket versioning metadata; no local persistence. Dependencies include cli, console color, JSON output, and the mc `Client` abstraction. Integration points include MinIO/S3 versioning APIs and shared globals set by `setGlobalsFromContext`. Risks include no trimming/validation of comma-separated prefixes in this layer and an apparent JSON tag typo for `ExcludeFolders`. No direct tests here.
