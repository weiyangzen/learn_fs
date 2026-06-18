# sources/test-tools/fio/trim.h

Purpose: public header for fio trim/discard support with compile-time stubs when trim is unavailable.

Important APIs/types: declares `get_next_trim()` and `io_u_should_trim()`. Defines `remove_trim_entry(td, ipo)`, which removes an `io_piece` from its trim list and decrements `td->trim_entries` if linked. When `FIO_HAVE_TRIM` is not defined, all three helpers are inline no-ops returning false or doing nothing.

Control flow/state: the real inline helper guards `flist_empty()` before deletion and uses `flist_del_init()` to avoid stale links. This is shared by trim selection and verify selection to keep trim-list membership independent from verify-list membership.

Dependencies/integration: includes fio list, iolog, compiler, type, and OS headers only in trim-enabled builds. Consumers can call the API unconditionally because the header supplies stubs.

Risks/test signals: correctness depends on `td->trim_entries` matching actual list membership. Tests should compile both trim-enabled and trim-disabled configurations and verify that no-op stubs do not evaluate unsupported fields.
