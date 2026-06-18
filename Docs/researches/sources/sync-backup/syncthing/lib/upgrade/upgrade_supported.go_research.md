# sources/sync-backup/syncthing/lib/upgrade/upgrade_supported.go

Purpose: build-enabled implementation for fetching release metadata, selecting upgrades, downloading archives, verifying signatures, and replacing the binary.

Important APIs and control flow: built when not `noupgrade` and not iOS. `upgradeClient` uses Syncthing dialer, TLS 1.2+, proxy, HTTP/2, and long read timeout. `FetchLatestReleases` GETs JSON with metadata limit. `SelectLatestRelease` sorts releases, skips prereleases unless allowed, prefers same-major/minor path before a later major when appropriate, and requires an asset prefix from `releaseNames`. `upgradeToURL` downloads/extracts to temp, renames current binary to `.old`, and renames temp into place with rollback on final rename failure. `readTarGz` and `readZip` scan bounded archive members/sizes for `syncthing`/`syncthing.exe` and `release.sig`. `verifyUpgrade` verifies the signature over `archiveName + "\n" + binary contents` with embedded signing key. `writeBinary` writes temp executable with 0755.

State and persistence: network metadata/downloads, temp files in binary directory, current binary rename, `.old` backup, embedded key verification.

Dependencies and integration: release API, `signature`, `tlsutil`, `dialer`, gopsutil OS version header, tar/zip/gzip.

Risks: partial upgrades depend on filesystem rename semantics. Archive limits and shallow binary path checks mitigate malicious archives. Tests cover version selection, not full download/extract/signature paths.
