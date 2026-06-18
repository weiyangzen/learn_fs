<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/pre-steps-macos/action.yml

Purpose: macOS wrapper around the shared `pre-steps` composite action.

Important APIs/types/functions: contains one step using `./.github/actions/pre-steps`.

Control flow: delegates all setup to the generic pre-step action.

State and persistence behavior: same environment mutations as `pre-steps`, mainly `GITHUB_ENV` settings.

Dependencies and integration points: used by macOS jobs after macOS-specific package/ulimit setup.

Risks: Linux-oriented commands inside `pre-steps`, especially `apt-get install lld`, are allowed to fail with `|| true`, but still add noise and depend on shell compatibility.

Test signals: downstream macOS build/test jobs receiving common GTest/CTest environment variables.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps-macos/action.yml -->
