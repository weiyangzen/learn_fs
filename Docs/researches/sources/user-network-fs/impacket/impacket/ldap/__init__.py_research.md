# sources/user-network-fs/impacket/impacket/ldap/__init__.py

Purpose: marks `impacket.ldap` as a package and contains only licensing comments, an empty description marker, and `pass`. It does not re-export LDAP classes or perform runtime setup.

Important APIs/types/functions: none. Consumers import concrete modules such as `impacket.ldap.ldap`, `ldapasn1`, and `ldaptypes`.

Control flow and state: no runtime logic, state, persistence, or I/O.

Dependencies and integration: package identity enables relative/import-package access for LDAP modules.

Risks and test signals: low risk. Tests only need to ensure package import succeeds and downstream explicit module imports remain available.
