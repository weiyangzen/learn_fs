# sources/sync-backup/git-crypt/git-crypt.hpp

Purpose: small global header defining the git-crypt version and exposing `argv0` for utility path resolution.

Important APIs/types/functions: `#define VERSION "0.8.0"` and `extern const char* argv0`.

Control flow: no runtime flow. `git-crypt.cpp` initializes `argv0`, and platform utilities read it to determine the executable path.

State/persistence behavior: `argv0` is process-global transient state. No persistent files are touched.

Dependencies/integration: included by CLI and utility code. Version text is used by the CLI and should align with documentation/release assets.

Risks/test signals: version drift between this header, manpage product name, tags, and release asset naming can confuse packaging. Tests should verify `git-crypt --version` output.
