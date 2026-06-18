# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsget.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsget.c

Purpose: Demonstrates querying domain/user policy modal information with `NetUserModalsGet()`.

Important APIs/types/functions: Handles `USER_MODALS_INFO_0/1/2/3`, including password age/length/history, role, primary server, domain SID/name, and lockout policy.

Control flow: Parses hostname and level, calls the API, switches on level to print policy fields, converts domain SID where present, frees the buffer, and exits.

State and persistence behavior: Read-only policy query.

Dependencies and integration points: Complements `user_modalsset` and account policy administration.

Risks: Units are printed as days/seconds based on sample assumptions. Unsupported levels are not explained.

Test signals: Query all supported levels before/after modal policy changes in a test domain.
