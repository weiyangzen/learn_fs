<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/stack.yaml -->
# sources/sync-backup/git-annex/stack.yaml

Purpose: default Stack build configuration for git-annex without Botan support.

Important settings: enables production, parallelbuild, assistant, torrentparser, benchmark, and ospath flags; disables magicmime, dbus, debuglocks, and `botan`. Sets `file-io` `os-string: true`, uses local package `'.'`, resolver `lts-24.26`, and extra deps `aws-0.25.2` and `file-io-0.2.0`.

Control flow and state: declarative input to Stack's solver/build process, with no persisted runtime state aside from Stack build caches.

Dependencies and integration points: Stack, Stackage LTS 24.26, git-annex's Cabal flags, and the listed extra deps.

Risks: resolver pinning stabilizes builds but needs maintenance for security/compiler updates. The disabled `magicmime`/`dbus` flags exclude optional integrations from this build profile.

Test signals: `stack build`, `stack test` if supported, and verification that Cabal flags match expected default build features.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/stack.yaml -->
