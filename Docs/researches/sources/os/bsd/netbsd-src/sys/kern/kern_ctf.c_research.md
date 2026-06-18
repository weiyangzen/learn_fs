# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ctf.c

Read completely: 247 lines.

Implements kernel/module CTF metadata lookup and optional decompression support for DTrace-style consumers. The file avoids depending on the CDDL CTF header structure by using known offsets into the CTF header bytes.

`mod_ctf_get()` first checks cached module-specific CTF state through `fbt_module_key`. If absent, it allocates `mod_ctf_t`, finds module symbol/string tables either from the ksyms module table or the module kobj, locates `.SUNW_ctf`, validates the CTF magic and version 2 or 3, determines whether the CTF payload is compressed, and either references the existing CTF section or allocates a decompressed buffer. Compressed data is inflated with zlib after copying the fixed-size header. On success, the metadata is cached on the module and returned.

`z_alloc()` and `z_free()` are zlib allocation wrappers using `M_TEMP`.

Risks and notes: compressed size calculation trusts CTF header offsets after only magic/version checks. `inflateEnd()` is not called after `inflateInit2()`. `mc->ctfcnt` is set to the original section size even when `mc->ctftab` points to the decompressed buffer. Several string/symbol count fields are marked `XXX TBD`.
