<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchpathcon.c -->
# sources/security-integrity/selinux/libselinux/src/matchpathcon.c

## Purpose
Provides the deprecated compatibility `matchpathcon*` API on top of modern `selabel` file-context lookup. It also tracks inode-to-spec associations for conflict diagnostics.

## Important APIs, Types, And Functions
Public entry points include `matchpathcon_init_prefix()`, `matchpathcon_init()`, `matchpathcon()`, `matchpathcon_index()`, `matchpathcon_fini()`, `selinux_file_context_verify()`, `selinux_lsetfilecon_default()`, and callback setters for printf, invalid-context checks, canonicalization, and flags. `compat_validate()` validates or canonicalizes lookup records. `realpath_not_final()` resolves parent paths while preserving a final symlink component.

## Control Flow
Initialization creates a thread-local `selabel_handle` with options derived from `set_matchpathcon_flags()`. Lookup resolves paths differently for symlinks and non-symlinks, then calls raw or translated `selabel_lookup`. Verification compares current raw xattr against expected raw context while ignoring user-field differences.

## State And Persistence Behavior
State is thread-local (`hnd`, options, context index array, `notrans`) plus a process hash table for inode/spec associations. Destructors free thread-local state. `selinux_lsetfilecon_default()` persists an xattr when a default label is found.

## Dependencies And Integration Points
Integrates with `selabel_open`, `selabel_lookup`, validation callbacks, xattr getters/setters, path canonicalization, and old `setfiles`-style conflict reporting.

## Risks And Test Signals
Risks include thread-local lifecycle, realpath behavior for missing symlink targets, inode hash conflicts, and deprecated compatibility callbacks. Tests should cover symlinks, relative paths, validation/canonicalization callbacks, no-match verification, ENOTSUP/ENOENT handling, and multi-thread init/fini.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchpathcon.c -->
