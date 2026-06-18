# sources/security-integrity/ecryptfs-utils/scripts/build-ubuntu.sh

Purpose: builds an Ubuntu source/binary package from a generated upstream release tarball.

Important APIs/commands: runs `release.sh --nosign`, moves `*.orig.tar.gz` into a fresh `ubuntu` directory, extracts it, copies Debian packaging from the original checkout, and invokes `debuild -uc -us`.

Control flow/state: deletes/recreates sibling `ubuntu`, moves release artifacts, and builds without signing.

Dependencies/integration: Debian packaging tools, `release.sh`, and expected directory naming.

Risks: destructive `rm -rf ubuntu`; assumes current working directory basename and tarball naming.

Test signals: successful `debuild` output.
