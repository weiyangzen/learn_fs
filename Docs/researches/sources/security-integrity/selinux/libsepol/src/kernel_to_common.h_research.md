# sources/security-integrity/selinux/libsepol/src/kernel_to_common.h

Purpose: internal header for kernel policy text conversion helpers. It defines static lookup data and declares the helper API implemented by `kernel_to_common.c` for use by policy.conf/CIL emitters.

Important APIs and types: exposes `STACK_SIZE`, fallback MLS/object constants (`DEFAULT_LEVEL`, `DEFAULT_OBJECT`), `selinux_sid_to_str`, `xen_sid_to_str`, `SELINUX_SID_SZ`, `XEN_SID_SZ`, the ordered `avtab_flavors[]` list, `AVTAB_FLAVORS_SZ`, opaque `struct strs`, formatting helpers, string-list helpers, ebitmap/name conversion helpers, stack helpers, `isids_to_strs`, `sort_ocontexts`, and `check_for_supported_policy`.

Control flow: this file has no runtime control flow, but the static arrays determine output order and naming for callers. `avtab_flavors[]` fixes the order for access-vector and type-rule emission, while SID tables provide stable names for numeric initial SIDs that are not stored in binary policy packages.

State and persistence: the arrays are translation-unit-local because they are `static const` in the header; each including C file receives its own copy. There is no persistent state, but changing these constants changes generated policy text and ABI-adjacent behavior for converters.

Dependencies and integration points: includes `stdio.h`, `stdarg.h`, `sys/types.h`, libsepol `avtab.h`, and `policydb.h`. It is included by `kernel_to_common.c` and `kernel_to_conf.c`; sibling emitters depend on the same prototypes and tables.

Risks: because large static arrays live in a header, every includer has a private copy; this is intentional for internal helpers but would be unsuitable for public ABI. SID mappings must remain synchronized with Linux/Xen kernel initial SID numbering. Adding or reordering `avtab_flavors[]` changes output ordering and can affect golden tests.

Test signals: compile all converter translation units with format-attribute checking enabled, verify no duplicate-symbol linkage issues from header-local arrays, and compare generated policy.conf output against expected SID and AV rule ordering.
