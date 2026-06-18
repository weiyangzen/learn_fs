# sources/security-integrity/selinux/libsepol/include/sepol/iface_record.h

Purpose: Declares the public record/key API for network interface contexts.

Important APIs and types: Opaque `sepol_iface_t` and key type; key create/unpack/extract/free; compare helpers; name get/set; interface and message context get/set; create/clone/free.

Control flow: Interface records represent `netifcon` entries with two contexts: one for the interface and one for received packets/messages.

State and persistence: Records own name/context fields until applied to policydb collection APIs.

Dependencies and integration points: Depends on context records and handles; collection APIs live in `interfaces.h`.

Risks: Two-context ownership can be confused by callers. Name identity must match policydb string keys exactly.

Test signals: Round-trip name/key behavior, both context fields, clone/free, and policydb query/modify validate the contract.
