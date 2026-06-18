## sources/object-store/minio-mc/cmd/update_nofips.go

Purpose: selects the standard release metadata endpoint for `mc update` builds without the `fips` build tag. It defines `mcReleaseInfoURL` as `mcReleaseURL + "mc.sha256sum"`.

Control flow is entirely compile-time through `//go:build !fips`. Runtime state is absent; the variable is consumed by `DownloadReleaseData` unless the caller supplies a custom release URL or Windows uses the `.exe.sha256sum` variant. Dependencies are limited to `mcReleaseURL`. The main risk is configuration drift with the FIPS file, because exactly one of the two URL definitions must compile. Test signal is build-matrix oriented rather than behavioral in normal unit tests.
