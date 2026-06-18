# sources/security-integrity/selinux/libselinux/src/compute_create.c

Purpose: Computes a default creation context for a source context, target context, object class, and optional object name by querying `selinuxfs/create`.

Important APIs/types/functions: exports `security_compute_create_name_raw()`, `security_compute_create_raw()`, `security_compute_create_name()`, and `security_compute_create()`. `object_name_encode()` percent-encodes object names for the kernel request format, preserving alnum and selected safe punctuation while mapping space to `+`.

Control flow: raw create computation formats `scon tcon class`, appends encoded object name if supplied, writes to `/create`, reads the resulting raw context, and duplicates it for the caller. Public wrappers translate contexts in and the returned context out.

State and persistence: no persistent state is modified.

Dependencies and integration: AVC `avc_compute_create()` can call the raw API and cache the resulting SID. Mapping uses `unmap_class()`.

Risks and test signals: object-name encoding is length-sensitive and byte-oriented. Tests should cover spaces, percent-encoded bytes, long names, null name, translation failures, and ENAMETOOLONG/EOVERFLOW behavior.
