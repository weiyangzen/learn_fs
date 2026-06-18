# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_common.c

Purpose: provides shared RQUOTA path normalization.

Important APIs/types/functions: exports `check_handle_lead_slash(char *quota_path, char *temp_path, size_t temp_path_size)`.

Control flow: if a quota path is absolute, it returns the original pointer. For relative/tag-like paths, it fetches the root pseudo export, reads the export full path under RCU/refstr protection, copies it to the caller buffer, adds a slash if needed, appends the quota path, and returns the buffer. Overlong paths or missing export/fullpath return `NULL`.

State and persistence: no persistent mutation. It takes and releases export and refstr references and uses caller-supplied temporary storage.

Dependencies and integration points: integrates RQUOTA handlers with export manager path lookup and the root pseudo export.

Risks and test signals: path length checks, root export absence, RCU/refstr lifetime, and relative path handling determine quota lookup correctness. Test absolute paths, relative paths, long paths, missing root pseudo export, and root fullpath without trailing slash.
