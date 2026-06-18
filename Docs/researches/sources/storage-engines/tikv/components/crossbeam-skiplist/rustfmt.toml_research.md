# sources/storage-engines/tikv/components/crossbeam-skiplist/rustfmt.toml

Purpose: This configuration deliberately leaves rustfmt at defaults to preserve the upstream `crossbeam-skiplist` style and reduce cherry-pick conflicts.

Important APIs and settings: There are no active rustfmt keys. The comments explain that the empty file is intentional.

Control flow: Not applicable; rustfmt reads the file and applies default formatting.

State and persistence behavior: The file is persistent repository formatting policy. It does not affect runtime state.

Dependencies and integration points: It integrates with developer formatting tools and CI formatting checks for this vendored component.

Risks: Future contributors may assume the file is accidentally empty and add local style settings, increasing divergence from upstream.

Test signals: Formatting stability is the only signal; no code tests depend on it.
