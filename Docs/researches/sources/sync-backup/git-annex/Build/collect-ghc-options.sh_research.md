# sources/sync-backup/git-annex/Build/collect-ghc-options.sh

Purpose: translates conventional C toolchain flags into GHC option flags so Haskell builds pass them through to linker/compiler/preprocessor stages.

Important APIs/types/functions: loops over `$LDFLAGS` emitting `-optl...`, `$CFLAGS` emitting `-optc...`, and `$CPPFLAGS` emitting `-optc-Wp,...`.

Control flow/state: pure stdout generator; no files are mutated. Word splitting follows shell whitespace semantics.

Dependencies/integration: used by the git-annex Makefile during cabal configure as `--ghc-options="$(shell Build/collect-ghc-options.sh)"`.

Risks/test signals: flags containing spaces or shell-sensitive quoting can be split incorrectly. Build failures in environments with custom flags are the primary signal.

Source research group: `subset-b-009122`.
