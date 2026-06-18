# sources/user-network-fs/nfs-utils/support/nfs/exports.c

Purpose: parser and emitter for NFS export entries, including export options, security flavors, transport security, squash lists, fsid/UUID, referrals/replicas, pNFS, and reexport integration.

Important APIs and data: `setexportent()`, `getexportent()`, `putexportent()`, `endexportent()`, `dupexportent()`, `mkexportent()`, `updateexportent()`, `secinfo_addflavor()`, `secinfo_show()`, `xprtsecinfo_show()`, `fix_pseudoflavor_flags()`, and `get_export_features()`. `flav_map` maps `krb5`, `krb5i`, `krb5p`, `unix`, `sys`, `null`, and `none`. Export defaults include read-only, root-squash, gathered writes, and no-subtree-check.

Control flow: `getexportent()` reads the path, optional default options beginning with `-`, then a client token with optional parenthesized options. It initializes defaults, parses options with `parseopts()`, canonicalizes the export path through `nfsd_realpath()`, and returns a static `struct exportent`. `parseopts()` tokenizes comma-separated options, sets/clears flags globally and on active security flavors, parses ID ranges, fsid/UUID, mountpoint, fsloc, `sec=`, `xprtsec=`, and `reexport=`, then normalizes pseudoflavor flags against kernel-supported feature masks.

State and persistence: uses static file name/handle, static returned export entries, and static squash arrays that are moved into export entries. `get_export_features()` caches `/proc/fs/nfsd/export_features`. Persistent input/output is `/etc/exports` or `/proc/fs/nfs/exports` style files via `XFILE`.

Dependencies and integration: depends on export flag definitions, `xio` tokenization, `xmalloc`, `xlog`, pseudoflavor constants, reexport database hooks, and `nfsd_path` realpath handling. It is central to `exportfs`, `mountd`, and kernel export cache population.

Risks: parser state is nonreentrant. `putexportent()` appears to use `e_nsquids` while printing `e_sqgids`, which can omit or overrun group squash ranges when UID and GID range counts differ. Option parsing mutates temporary strings and global squash pointers in ways sensitive to early failures. `fsid=` must precede `reexport=`, which should be documented/tested for user-facing diagnostics.

Test signals: export lines with default options, empty/default clients, missing option warnings, each flag pair, sec flavor grouping, xprtsec modes, squash UID/GID ranges, fsid root/numeric/UUID, reexport strategies, malformed options, path canonicalization, and round-trip `putexportent()`.
