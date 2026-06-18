# sources/sync-backup/git-annex/Makefile

Purpose: top-level git-annex build, install, test, documentation, clean, and packaging orchestration.

Important APIs/types/functions: targets include `build`, `install`, `install-home`, `build-dependencies`, `tmp/configure-stamp`, `dev`, `prof`, executable symlink targets, `install-*`, `test`, `retest`, `tags`, `mans`, `docs`, `clean`, standalone Linux packaging, Debian standalone packaging, OS X app packaging, and `distributionupdate`.

Control flow/state: chooses `cabal` by default or `stack` when requested, configures once into `tmp/configure-stamp`, builds `git-annex`, links related command names to the main binary, installs docs/completions, and generates platform packages under `tmp`. Several targets patch or reset packaging state using quilt/git commands.

Dependencies/integration: integrates Cabal/Stack/GHC, ikiwiki, rsync, hasktags, Debian packaging tools, hdiutil/install_name_tool on macOS, and helper Haskell builders under `Build/`.

Risks/test signals: large orchestration blast radius; environment differences in Cabal layouts, Stack dist dirs, docs tools, or packaging tools can break targets. `make test` and CI configs provide the main validation path.

Source research group: `subset-b-009122`.
