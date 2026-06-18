# sources/security-integrity/audit-userspace/auparse/ellist.h

Purpose: Declares the auparse event record linked-list type and hidden list operations.

Important APIs, types, and functions: Defines `event_list_t` with `rnode *head`, `rnode *cur`, `cnt`, `au_event_t e`, and event-level `cwd`. Provides inline `aup_list_get_cnt()`, `aup_list_first()`, and `aup_list_get_cur()`. Declares create/clear/next/append/set-event/goto-record/first-field functions.

Control flow: Header controls cursor access patterns through inlines; implementation flow is in `ellist.c`.

State and persistence: `event_list_t` is mutable in-memory parser state for one event. It owns event host and CWD pointers after setup/append.

Dependencies and integration points: Includes `auparse-defs.h`, `nvlist.h`, and private visibility macros. Used by `auparse.c`, `expression.c`, and interpretation code.

Risks and edge cases: Cursor state is embedded in the list, so nested iteration or concurrent use of the same parser state can disturb callers. Ownership is not obvious from the struct alone; callers must use `aup_list_clear()`.

Test signals: Parser traversal tests covering `auparse_first_record()`, `auparse_next_record()`, and field iteration indirectly validate this interface.
