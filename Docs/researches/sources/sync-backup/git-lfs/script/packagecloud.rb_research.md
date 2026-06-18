# sources/sync-backup/git-lfs/script/packagecloud.rb

Purpose: uploads built `.rpm` and `.deb` packages under `repos/` to PackageCloud distro targets.

Important APIs/functions: `DistroMap#distro_name_map`, global `$client`, `$distro_id_map`, `distro_names_for`, `Packagecloud::Credentials`, `Packagecloud::Client`, and `Packagecloud::Package`.

Control flow: validates `PACKAGECLOUD_TOKEN`, loads `packagecloud-ruby`, constructs credentials, discovers package files, skips `repo-release`, maps each filename to equivalent distro names by substring pattern, caches distribution IDs, and uploads each package. Duplicate filename errors are ignored; other upload failures raise.

State/persistence behavior: no local writes beyond gem loading. Remote PackageCloud package state is mutated by uploads.

Dependencies/integration: release packaging pipeline, `script/lib/distro.rb`, PackageCloud credentials, and package naming conventions that include distro keys.

Risks: filename substring matching can misclassify packages if paths change. Duplicate handling depends on exact PackageCloud error JSON. Global variables make isolated testing harder.

Test signals: upload logs, PackageCloud package presence, and failure on missing distro IDs or non-duplicate API errors.
