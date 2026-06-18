## sources/object-store/minio-mc/cmd/update_fips.go

Purpose: selects the FIPS release metadata endpoint for `mc update` builds compiled with the `fips` build tag. It defines `mcReleaseInfoURL` as `mcReleaseURL + "mc.fips.sha256sum"`.

Control flow is compile-time only: the Go build constraint `//go:build fips` ensures this file replaces the non-FIPS URL definition. State and persistence are absent; it only influences network fetches made by `DownloadReleaseData`. Dependencies are the package-level `mcReleaseURL` constant from `update-main.go`. Integration risk is mis-building a FIPS binary with the wrong tag, which would fetch ordinary checksums. Test signal would require build-tag-specific compile or unit checks.
