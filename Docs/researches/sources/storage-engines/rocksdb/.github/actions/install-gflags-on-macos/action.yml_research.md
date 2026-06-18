<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags-on-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-gflags-on-macos/action.yml

Purpose: Installs gflags on macOS CI runners through Homebrew.

Important APIs/types/functions: single bash step `HOMEBREW_NO_AUTO_UPDATE=1 brew install gflags`.

Control flow: package installation runs before macOS build/test jobs that configure RocksDB with gflags support.

State and persistence behavior: mutates the ephemeral runner's Homebrew installation only.

Dependencies and integration points: used by macOS PR and Java jobs. Integrates with make/CMake detection of gflags.

Risks: Homebrew package availability, bottle changes, or preinstalled conflicts can break CI. Auto-update is disabled for speed but can leave outdated metadata.

Test signals: later build/link steps and tools requiring gflags are the validation signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags-on-macos/action.yml -->
