# sources/security-integrity/ecryptfs-utils/scripts/release.sh

Purpose: creates and optionally signs an upstream release tarball and prints follow-up Launchpad/Debian release instructions.

Important APIs/functions: `error()` aborts; checks `debian/changelog` contains `unreleased`; extracts current version; runs autogen/configure/make dist; renames tarball to Debian orig format; optionally signs with GPG; tags with bzr; builds source package with copied Debian directory; prints next-version commands.

Control flow/state: writes tarballs in parent directory, mutates bzr tags, extracts release tarball, and may run `debuild -S`.

Dependencies/integration: Autotools, GPG, Bazaar, Debian devscripts, Launchpad workflow.

Risks: old bzr/Launchpad assumptions, version extraction by sed, and signing/tagging side effects. `--nosign` exits before tagging/package steps.

Test signals: successful tarball, signature, bzr tag, and source package.
