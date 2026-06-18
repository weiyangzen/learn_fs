# sources/security-integrity/selinux/libsepol/src/ibendport_record.c

Purpose: implements the high-level `sepol_ibendport_t` and `sepol_ibendport_key_t` record API for SELinux InfiniBand end-port contexts, keyed by IB device name and port.

Important APIs and functions: key APIs include `sepol_ibendport_key_create`, `sepol_ibendport_key_unpack`, `sepol_ibendport_key_extract`, and `sepol_ibendport_key_free`. Record APIs include `sepol_ibendport_create`, `sepol_ibendport_clone`, `sepol_ibendport_free`, compare functions, port get/set, device-name get/set, context get/set, and `sepol_ibendport_alloc_ibdev_name`.

Control flow: creation allocates zeroed record/key objects, copies device names into fixed `IB_DEVICE_NAME_MAX` buffers, and stores port integers. Cloning deep-copies device name and context. Setters allocate new storage before replacing existing fields. Context assignment clones the supplied `sepol_context_t`.

State and persistence behavior: records are heap objects owned by callers. Device names and contexts are deep-owned by records/keys. No policydb persistence occurs here; low-level policy insertion is handled by `ibendports.c`.

Dependencies and integration points: includes policydb for `IB_DEVICE_NAME_MAX`, internal context conversion header for context cloning/freeing, `ibendport_internal.h`, and diagnostics. It feeds the collection APIs that convert to and from `ocontext_t`.

Risks: device names are truncated with `strncpy` to `IB_DEVICE_NAME_MAX - 1`, so callers may not notice truncation. Compare order sorts primarily by port, using device-name comparison only when ports match/equal checks need it, which may differ from lexical device-first expectations. Error messages include minor wording mistakes but not behavior impact.

Test signals: create/free keys and records, long device-name truncation, compare ordering by port and name, clone independence, context setter deep-copy behavior, allocation failures, and key extraction from records with unset fields.
