<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-folly/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/cache-folly/action.yml

Purpose: Composite action that caches the Folly getdeps install directory for debug Folly builds.

Important APIs/types/functions: output `cache-hit`; steps compute `FOLLY_MK_HASH`, compute `FOLLY_INSTALL_DIR` via `third-party/folly/build/fbcode_builder/getdeps.py show-inst-dir`, and call `actions/cache@v4` on the normalized installed directory.

Control flow: shell steps expose hash and install path through `GITHUB_OUTPUT`; the cache step uses runner OS/arch, container image, `folly.mk` hash, and `PORTABLE` mode in the key.

State and persistence behavior: persists the getdeps installed tree across CI runs. It does not cache source checkouts or download tarballs; those are handled elsewhere.

Dependencies and integration points: used before `build-folly` in Folly CI jobs. Depends on checked-out Folly sources from `setup-folly`, Python getdeps, `md5sum`, and `actions/cache`.

Risks: the action assumes the getdeps path contains `installed/folly` so the `sed` normalization is valid. Container image can be empty on non-container jobs, affecting key shape. It is only intended for debug Folly builds.

Test signals: `steps.cache-folly-build.outputs.cache-hit` drives whether `build-folly` runs; cache restore/save logs are the main validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-folly/action.yml -->
