# sources/user-network-fs/samba/source4/lib/registry/patchfile.c

`patchfile.c` implements registry diff generation, patch format dispatch, and patch application callbacks. `reg_generate_diff_key()` recursively compares old and new registry keys, emitting add/delete key and set/delete value callbacks. `reg_generate_diff()` iterates all predefined HKEY roots. `reg_diff_load()` detects PReg files by `PReg` header and otherwise treats input as `.REG`. `reg_diff_apply()` wires callbacks that create/delete absolute keys and set/delete values on a `registry_context`.

Control flow is callback-driven: generation is backend-agnostic, and loading delegates parsing to format-specific modules. Apply creates intermediate keys for additions, ignores missing deleted parent keys, and repeatedly deletes value index 0 for "delete all values".

Persistence is whatever registry backend the context represents; patch application mutates it. Risks include non-transactional patch application, recursive diff order interactions, ignored callback return values in some generation paths, memory ownership around value names/data, and type/data comparisons relying on backend canonicalization. Test signals include round-trip diff/apply between two hives, PReg and `.REG` loaders, deletion of nested keys, default values, and failed mid-patch behavior.
