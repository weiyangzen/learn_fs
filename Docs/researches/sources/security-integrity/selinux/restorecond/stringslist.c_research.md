# sources/security-integrity/selinux/restorecond/stringslist.c
# sources/security-integrity/selinux/restorecond/stringslist.c

Purpose: small sorted linked-list utility for strings and wildcard matching.

Important APIs and control flow: `strings_list_add()` inserts unique strings in sorted order. `strings_list_find()` checks each pattern using `fnmatch()` and reports exact-match status through an output flag. `strings_list_free()` releases nodes. `strings_list_diff()` compares two sorted lists for any difference. `strings_list_print()` dumps entries. A `TEST` main provides ad-hoc checks.

State and persistence: in-memory linked lists only.

Dependencies and integration points: used by `watch.c` to track watched filenames per directory and by `utmpwatcher.c` to track logged-in users.

Risks and test signals: `strings_list_find()` assumes `exact` is non-null; callers comply. The `TEST` block appears stale (`strings_list_find` called with too few args), so compile-time test mode may not build without updates.
