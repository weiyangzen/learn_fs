## sources/object-store/minio-mc/cmd/version-info.go

Purpose: implements `mc version info`, reporting bucket versioning status, MFADelete, excluded prefixes, and folder exclusion. Important surfaces are `versionInfoCmd`, `versioningInfoMessage`, `checkVersionInfoSyntax`, and `mainVersionInfo`.

Control flow requires one target, initializes a client, calls `client.GetVersion`, copies returned status fields into the output message, and prints either JSON or colored text. State is read-only remote bucket metadata. Dependencies include cli, colorjson, console, and the client versioning API. Integration points are the `version` command group and global output settings. Risks are mostly reporting drift: empty status is rendered as un-versioned, and excluded prefix structs are flattened to strings. Test signal is absent in this subset; useful coverage would include enabled, suspended, and unconfigured buckets.
