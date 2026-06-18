# sources/user-network-fs/samba/source4/lib/policy/gp_ini.c

`gp_ini.c` parses and queries GPT INI files. `gp_parse_ini()` calls Samba's `pm_process()` parser with `gp_add_ini_section()` and `gp_add_ini_param()` callbacks to build a `gp_ini_context` containing sections and key/value arrays. `gp_get_ini_string()` and `gp_get_ini_uint()` scan the parsed structure for a section/name pair and return a string pointer or `atol()`-converted integer.

The file has no external persistence beyond reading the supplied INI path; parsed state lives under the caller's talloc context. It depends on `samba_util.h` and `policy.h`. Control flow is simple but strict: parameters before any section fail parsing because `cur_section` remains `-1`.

Risks include linear lookups, duplicate sections or keys returning the first match, unsigned integer conversion through `atol()` without range or error validation, and `gp_parse_ini()` callers needing to pass the actual file path. In `gp_manage.c`, a computed `GPT.INI` path is not used when calling `gp_parse_ini()`, which looks suspicious. Test signals should include normal GPT.INI, missing section/name, malformed files, duplicate keys, and large numeric values.
