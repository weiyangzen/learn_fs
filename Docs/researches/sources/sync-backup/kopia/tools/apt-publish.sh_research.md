<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/apt-publish.sh -->
# sources/sync-backup/kopia/tools/apt-publish.sh

This script publishes Debian/APT artifacts to a Google Cloud Storage package host. It requires `PACKAGES_HOST`, takes a package directory, signs/arranges packages using a fixed GPG key ID, and handles stable/testing distribution paths with retention for unstable packages.

Control flow exits without publishing when `PACKAGES_HOST` is unset, then prepares apt repository metadata and copies results to `gs://$PACKAGES_HOST/apt`. It distinguishes stable and testing distributions based on package/version inputs and keeps a bounded number of unstable `.deb` artifacts.

State is local package metadata plus remote GCS repository contents. Dependencies are bash, GPG, apt tooling, gsutil/gcloud environment, and naming conventions. Risks include accidental publish to wrong bucket, fixed key availability, retention deleting desired artifacts, and `set -e` stopping mid-publish without rollback. Test signals are likely release-pipeline execution rather than unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/apt-publish.sh -->
