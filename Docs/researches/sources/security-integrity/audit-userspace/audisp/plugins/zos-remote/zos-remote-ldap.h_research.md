# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.h

Purpose: declares the z/OS Remote-services LDAP wire contract, constants, return codes, session struct, and API.

Important APIs and data: defines audit request/response OIDs, request version, ASN.1 tag constants, event and qualifier codes, relocation field constants, z/OS major response codes, standard field sizes, ICTX error codes, `ZOS_REMOTE`, and LDAP submit/init/destroy APIs.

Control flow: no implementation; comments document the ASN.1 request/response structures and meaning of major/minor codes.

State and persistence: `ZOS_REMOTE` holds mutable connection/session state and plaintext credentials in memory.

Dependencies and integration: includes `lber.h` and `ldap.h`; consumed by LDAP implementation, logging helpers, and zOS plugin code that builds BER requests.

Risks: constants are protocol contracts; changing them breaks compatibility with z/OS Remote-services. Typo in "Reguestor" comment is harmless but field meanings must remain exact.

Test signals: compile tests plus BER construction/decoding tests against expected OIDs, version, field sizes, and return-code mapping.
