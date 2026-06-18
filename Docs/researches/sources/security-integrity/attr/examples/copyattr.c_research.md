## sources/security-integrity/attr/examples/copyattr.c

Purpose: sample file-manager style extended-attribute copy program.

It defines an `error_context`, simplistic quote/free callbacks, a filter `is_user_attr` that allows only `user.*`, and `main` that calls `attr_copy_file(from,to,...)` when available. State is local process state only. Dependencies are public `attr/error_context.h` and `attr/libattr.h`, locale setup, and libc allocation. Risks include a leak/bug in `quote` where `pathname` is duplicated twice and the first duplicate is lost, minimal i18n, and compile-time feature guards that can disable the copy call. Test signal is manual copying of user xattrs and error callback behavior.
