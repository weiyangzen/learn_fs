# sources/security-integrity/selinux/libsepol/src/iface_record.c

Purpose: implements high-level `sepol_iface_t` and `sepol_iface_key_t` records for SELinux network interface contexts. Each interface has a name, an interface context, and a message context.

Important APIs and functions: key APIs include `sepol_iface_key_create`, `sepol_iface_key_unpack`, `sepol_iface_key_extract`, and `sepol_iface_key_free`. Record APIs include `sepol_iface_create`, `sepol_iface_get_name`, `sepol_iface_set_name`, `sepol_iface_get_ifcon`, `sepol_iface_set_ifcon`, `sepol_iface_get_msgcon`, `sepol_iface_set_msgcon`, `sepol_iface_clone`, `sepol_iface_free`, and compare functions.

Control flow: key and name setters duplicate strings. Context setters clone supplied contexts before replacing existing ones. Clone creates a new record, copies the name, and deep-clones both contexts when present.

State and persistence behavior: records are caller-owned heap objects with owned name and context pointers. No policydb state is changed here.

Dependencies and integration points: depends on internal context APIs and public interface headers. `interfaces.c` uses these objects to convert to/from `OCON_NETIF` entries.

Risks: setters assume non-NULL input strings/contexts unless lower layers handle NULL. Compare is simple `strcmp`, so NULL names are unsafe. Callers must free keys/records to avoid leaks.

Test signals: key extraction, create/free, name setter ownership, compare ordering, context setter deep-copy behavior for both contexts, clone independence, and failure handling when context clone or string allocation fails.
