# sources/security-integrity/selinux/libsepol/include/sepol/ibendport_record.h

Purpose: Declares the public record/key API for InfiniBand end port security contexts.

Important APIs and types: Opaque `sepol_ibendport_t` and key type; compare/key create/unpack/extract/free; device-name allocation/get/set, port get/set, context get/set, create/clone/free.

Control flow: Keys are formed from IB device name plus port. Records carry the same identity and a `sepol_context_t`.

State and persistence: Record state is heap-owned until applied to a policydb through `ibendports.h`.

Dependencies and integration points: Depends on context records and handles; maps to `OCON_IBENDPORT` internals in policydb.

Risks: Device names have policydb maximum-length constraints enforced lower down. Context ownership must be clear when setting/cloning records.

Test signals: Key round trips, modify/query through policydb, clone/free, and invalid device/port cases are useful tests.
