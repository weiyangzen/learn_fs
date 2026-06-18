# sources/object-store/minio/cmd/update.go

Implements MinIO update discovery, binary download, checksum/signature verification, and self-update commit. It also detects deployment environments for update instructions and User-Agent fields.

Core APIs include release/time conversion helpers, `GetCurrentReleaseTime`, environment detectors (`IsDocker`, `IsDCOS`, `IsKubernetes`, `IsBOSH`, `IsSourceBuild`, `IsPCFTile`), `getHelmVersion`, `getUserAgent`, `downloadReleaseURL`, `parseReleaseData`, `getLatestReleaseTime`, `getDownloadURL`, `downloadBinary`, `verifyBinary`, and `commitBinary`. `updateInProgress` serializes verify/commit paths.

Control flow fetches release checksum metadata with update transport, parses `sha256 minio.RELEASE...`, chooses deployment-specific update guidance, downloads raw and zstd-compressed binary bytes, verifies checksum/minisign with `selfupdate`, and commits staged updates. State effects are executable metadata reads and self-update staging/commit; network dependencies include MinIO release URLs and minisign files. Risks include release parsing drift, environment misclassification, memory buffering of update binaries, signature URL mutation, and partial updater coverage. Tests cover parsing, download URL selection, HTTP metadata fetch, parse errors, and Helm labels, but not self-update apply/commit.
