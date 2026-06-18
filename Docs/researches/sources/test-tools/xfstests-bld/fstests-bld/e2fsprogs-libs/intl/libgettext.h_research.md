<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgettext.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgettext.h

## Purpose
This older public gettext header declares gettext APIs and macro fallbacks for projects using the bundled implementation or systems with catgets/gettext variants.

## Important APIs, Types, and Functions
It defines `__USE_GNU_GETTEXT`, fallback `LC_MESSAGES`, `struct _msg_ent`, `gettext_noop`, prototypes for `gettext`, `dgettext`, `dcgettext`, `textdomain`, and `bindtextdomain`, plus double-underscore suffixed variants. Under `ENABLE_NLS`, macros may map `gettext` to `dgettext` and `dgettext` to `dcgettext`. Without NLS, macros return original strings or arguments.

## Control Flow
There is no runtime flow. Preprocessor branches select system gettext/catgets behavior and may define a GCC constant-string caching macro for `dcgettext` using `_nl_msg_cat_cntr`.

## State and Persistence
No state is stored in the header, but the caching macro introduces static per-call-site variables in compiled code when enabled.

## Dependencies and Integration Points
It depends on `sys/types.h`, optional `locale.h`, `ENABLE_NLS`, `HAVE_CATGETS`, `HAVE_GETTEXT`, `HAVE_DCGETTEXT`, and `_nl_msg_cat_cntr`. It is marked obsolete in newer gettext distribution lists but still present for compatibility.

## Risks
Macro redirection can surprise callers taking function addresses or defining identifiers with the same names. The old GCC caching extension embeds static state at call sites and relies on `_nl_msg_cat_cntr` invalidation.

## Test Signals
Compile consumers with `ENABLE_NLS` on/off, with and without `HAVE_GETTEXT`/`HAVE_DCGETTEXT`, and verify macros and prototypes do not conflict with system `<libintl.h>`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgettext.h -->
