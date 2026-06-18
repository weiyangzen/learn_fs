# sources/security-integrity/selinux/scripts/release
# sources/security-integrity/selinux/scripts/release

Purpose: release automation for SELinux project component tarballs and wiki release text.

Important APIs and control flow: runs from repo root, clones the wiki if missing, reads top-level `VERSION`, defines release component list, creates annotated top-level tag and component tags if absent, archives each component with versioned prefix, signs tarballs with `gpg -b -a`, archives/signs full repository snapshot, and prints Markdown release links/checksums plus git push/wiki instructions.

State and persistence: creates git tags, `releases/$RELEASE_TAG` directory, tarballs, detached signatures, and optionally a sibling wiki clone.

Dependencies and integration points: maintainer-only workflow depending on git, gpg, sha256sum, component VERSION files, and GitHub release/wiki conventions.

Risks and test signals: tagging/signing are side-effectful; reruns warn on existing tags but still recreate release directory. No tests; correctness is manual review of generated assets and checksums.
