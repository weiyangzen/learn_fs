# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_mech2file.c

Purpose: maps a GSS mechanism OID to the short kernel/cache mechanism name used by server gssd.

Important APIs and data: `char *mech2file(gss_OID mech)` scans the static `m2f` table. The only configured mapping is the Kerberos V5 OID to `"krb5"`. `g_OID_equal` compares length and bytes.

Control flow: `do_svc_downcall()` and `get_ids()` call this to convert the accepted mechanism into the name used in procfs downcalls and nfsidmap calls. Unknown mechanisms return `NULL`, causing request failure paths in callers.

State and persistence: no mutable state. The returned pointer refers to static storage in `m2f`.

Dependencies and integration: depends on GSSAPI OID layout and the kernel/server idmapping convention that Kerberos is addressed as `krb5`.

Risks: adding a new mechanism requires updating this static table and ensuring all downstream idmapping/downcall formats support it. The exported prototype is local rather than in a header, so mismatches can compile unnoticed on permissive compilers. Test signals include known krb5 OID mapping, unknown OID rejection, and null/empty OID robustness.
