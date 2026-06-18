<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/stack-botan.yaml -->
# sources/sync-backup/git-annex/stack-botan.yaml

Purpose: Stack build configuration for git-annex with Botan crypto support enabled.

Important settings: sets `git-annex` flags for production, parallelbuild, assistant, torrentparser, benchmark, ospath, and `botan: true`; disables magicmime, dbus, debuglocks. Sets `file-io` `os-string: true`. Uses package `'.'`, resolver `lts-24.26`, and extra deps `aws-0.25.2`, `file-io-0.2.0`, `botan-low-0.2.0.1`, and `botan-bindings-0.3.0.0`.

Control flow and state: declarative Stack configuration consumed by `stack build`; it affects dependency solving and Cabal flags but has no runtime state.

Dependencies and integration points: Haskell Stack, Stackage LTS 24.26, local git-annex Cabal flags, and Botan Haskell bindings/native Botan availability.

Risks: Botan deps can require compatible system libraries/headers. Divergence from `stack.yaml` is only the Botan flag/deps, so both files must stay aligned when resolver or shared deps change.

Test signals: `stack build --stack-yaml stack-botan.yaml`, inspect configured Cabal flags, and run crypto-related tests that require Botan.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/stack-botan.yaml -->
