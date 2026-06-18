## sources/test-tools/fio/ci/common.sh

Purpose: shared Bash helper for CI target detection.

Important API and flow: `set_ci_target_os()` preserves existing `CI_TARGET_OS` and `CI_TARGET_ARCH` when set. Otherwise it derives `CI_TARGET_OS` from `OSTYPE` (`linux`, `macos`, `windows`, `bsd`, or empty fallback) and derives `CI_TARGET_ARCH` from `uname -m`.

State and persistence: exports no files; it updates shell variables in the caller's process because it is sourced.

Dependencies and integration: used by install and build scripts to share consistent platform naming. It assumes Bash syntax (`function`, `[[ ]]`) and therefore should be sourced only by Bash scripts.

Risks and test signals: `OSTYPE` pattern coverage is coarse, especially for BSD or unusual shells. The function intentionally does not overwrite workflow-provided targets, so matrix correctness depends on GitHub Actions configuration. Build/install dispatch success is the practical test signal.
