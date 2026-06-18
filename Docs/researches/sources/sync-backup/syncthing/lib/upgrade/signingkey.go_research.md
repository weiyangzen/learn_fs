# sources/sync-backup/syncthing/lib/upgrade/signingkey.go

Purpose: embeds the public signing key used to verify downloaded upgrade archives.

Important APIs and control flow: uses `go:embed signingkey.pem` to expose `SigningKey []byte`. Upgrade verification passes this key to `signature.Verify`.

State and persistence: key is embedded into the binary at build time.

Dependencies and integration: depends on Go embed and must match release signing infrastructure/stsigtool.

Risks: changing this key without synchronized release signing breaks all built-in upgrades. No tests in this subset directly verify the embedded key.
