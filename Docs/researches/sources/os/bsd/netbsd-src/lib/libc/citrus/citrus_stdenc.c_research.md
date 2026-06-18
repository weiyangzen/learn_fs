# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.c

Read completely: 199 lines.

This file implements opening and closing Citrus standard-encoding modules. It defines `_citrus_stdenc_default` backed by `NONE`, and, when `_I18N_DYNAMIC` is enabled, dynamically loads encoding modules, resolves their `stdenc_getops` entry point, validates the operation table, allocates traits, and calls the module initializer.

Key behavior: opening `"NONE"` returns the singleton default object. Dynamic modules get their own `_citrus_stdenc` with copied ops and traits. Older ABI operation tables are patched by assigning a default `get_state_desc` that returns `EOPNOTSUPP`.

Important interactions: used by `iconv_std` to open source and destination encodings from ESDB records. Includes `citrus_none.h` for the default encoding and `citrus_module.h` for dynamic loading.

Security/reliability notes: the loader validates required callbacks before use and unwinds partially initialized objects through `_citrus_stdenc_close`. Dynamic module loading makes module path/name control security-sensitive outside this file.
