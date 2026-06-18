# sources/security-integrity/selinux/scripts/make-update
# sources/security-integrity/selinux/scripts/make-update

Purpose: creates a component tarball for updating release assets.

Important APIs and control flow: requires `last-release-date` and `package-to-update`, creates `../update-$TAG`, verifies package directory exists, reads package `VERSION`, tags `PKG-VERSION`, creates a gzipped git archive with prefix, and prints wiki download link plus SHA256.

State and persistence: creates a git tag and archive under `../update-$TAG`.

Dependencies and integration points: release-maintainer helper relying on git, gzip, and sha256sum.

Risks and test signals: unconditionally tags without checking existing tag conflicts and does not sign artifacts. No tests.
