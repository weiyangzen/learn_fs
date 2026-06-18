# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/mail.c

- Role: Defines mailbox `From ` line regexes and simple parse/print helpers.
- Key functions: `print_header`, `print_remote_header`, and `parse_header`.
- Integration: Used by upas components needing Unix mbox-style header handling.
- Risks/notes: `parse_header` handles quoted sender names simply and does not perform full RFC822 parsing.
