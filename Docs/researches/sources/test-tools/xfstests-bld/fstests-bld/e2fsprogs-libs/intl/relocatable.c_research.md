# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.c

Purpose: implements optional relocatable installation-prefix rewriting for gettext/libintl packages.

Important APIs and control flow: under `ENABLE_RELOCATABLE`, `set_relocation_prefix()` stores original/current prefixes and notifies dependent charset/iconv/intl libraries. `compute_curr_prefix()` derives a current prefix from an original prefix, original install directory, and current pathname by stripping matching relative path components. For PIC shared libraries, platform-specific code locates the loaded library path using Win32 `DllMain` or Linux `/proc/self/maps`. `relocate(pathname)` lazily initializes shared-library prefixes when needed and rewrites paths beginning with `orig_prefix` to `curr_prefix`.

State and persistence: static `orig_prefix`, `curr_prefix`, lengths, optional `shared_library_fullname`, and initialization flags persist. Returned relocated strings may be newly allocated and intentionally leaked unless callers cache them.

Dependencies and integration: used by path-building code for catalogs and dependent libraries. Handles Unix, Win32, OS/2, and DOS path rules.

Risks and test signals: prefix memory is not freed, `/proc/self/maps` parsing is Linux/glibc-specific, and path comparison assumptions can fail for unusual installs. Test equal prefixes, moved trees, root prefixes, Windows drive paths, PIC library detection, and disabled relocation.
