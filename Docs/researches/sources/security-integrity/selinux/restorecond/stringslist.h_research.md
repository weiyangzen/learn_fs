# sources/security-integrity/selinux/restorecond/stringslist.h
# sources/security-integrity/selinux/restorecond/stringslist.h

Purpose: declares the `stringsList` linked-list structure and operations.

Important APIs and types: `struct stringsList { struct stringsList *next; char *string; }` plus add, find, diff, print, and free functions.

State and persistence: in-memory list ownership is manual; callers must free via `strings_list_free()`.

Dependencies and integration points: included by restorecond watch and utmp modules.

Risks and test signals: no const ownership annotations; API relies on callers understanding that strings are duplicated on add. No direct tests.
