# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.h

Purpose: declares or disables the relocatable path API.

Important APIs/types/functions: when `ENABLE_RELOCATABLE` is enabled, it declares exported `set_relocation_prefix(orig_prefix, curr_prefix)`, `relocate(pathname)`, and `compute_curr_prefix(orig_installprefix, orig_installdir, curr_pathname)`. It defines `RELOCATABLE_DLL_EXPORTED` for MSVC DLL builds. When relocation is disabled, `relocate(pathname)` is a macro identity function.

State and persistence: no state in the header; implementation state lives in `relocatable.c`.

Dependencies and integration: included by code that wants installation paths to survive tree moves without conditionalizing call sites.

Risks and test signals: callers must handle the dual nature of `relocate`: identity macro when disabled, possibly allocated/leaking pointer when enabled. Test both configure modes and C++ inclusion.
