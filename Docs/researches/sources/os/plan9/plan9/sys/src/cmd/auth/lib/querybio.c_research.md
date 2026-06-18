# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/querybio.c

Prompts interactively for account biography metadata. It first loads existing data with `rdbio`, then prompts for post id, full name, department, user email, sponsor email, and additional emails.

`defreadln` supports defaults, required fields, and clearing optional fields with a leading space. `querybio` returns whether any field changed.
