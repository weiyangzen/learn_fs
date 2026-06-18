# sources/user-network-fs/samba/source3/lib/privileges.h

## Purpose
This header declares the source3 privilege management API implemented by `privileges.c`. It is the include point for code that needs to query, enumerate, grant, revoke, create, or delete privilege records associated with SIDs.

## Important APIs, Types, And Functions
It includes `../libcli/security/privileges.h` for core privilege definitions and declares functions for SID-list privilege aggregation, conversion to `PRIVILEGE_SET`, account enumeration, privilege-specific SID enumeration, grant/revoke by name or LSA privilege set, account create/delete, privileged-SID check, and granting all privileges.

## Control Flow
There is no runtime control flow in the header. It fixes function signatures and exposes Samba's `NTSTATUS`/boolean return conventions to callers.

## State And Persistence
No state is defined in the header. Persistence is handled by the implementation in the account policy database under `PRIV_<SID>` keys.

## Dependencies And Integration Points
Callers must have Samba security types such as `struct dom_sid`, `PRIVILEGE_SET`, `struct lsa_PrivilegeSet`, and `enum sec_privilege` visible through included headers. The API integrates with LSA server code, passdb/account-policy code, and administrative tools.

## Risks And Test Signals
Header risks are ABI/API drift with `privileges.c` and missing prototypes for new implementation helpers. Build tests should compile all callers with this header, and functional tests belong with the implementation.
