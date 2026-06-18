# sources/user-network-fs/samba/source3/lib/smbconf/smbconf_init.c

## Purpose
This file implements the smbconf backend dispatcher. It parses a configuration source string and initializes the registry or text/file backend.

## Important APIs, Types, And Functions
`smbconf_init(TALLOC_CTX *mem_ctx, struct smbconf_ctx **conf_ctx, const char *source)` is the only function. It recognizes `registry:`/`reg:` and `file:`/`txt:` prefixes, accepts empty path after the colon as NULL, and falls back to text backend behavior for unprefixed strings or unknown prefixed strings that may be file names containing colons.

## Control Flow
The function validates `conf_ctx` and nonempty source, duplicates the source on a stackframe, splits at the first colon, and dispatches to `smbconf_init_reg()` or `smbconf_init_txt()`. If there is no separator and no known backend, it treats the whole source as a file path. If there is an unknown backend with a separator, it tries the original string as a file path.

## State And Persistence
No persistent state is stored here. It creates backend-specific `smbconf_ctx` objects whose state and persistence are owned by the selected backend.

## Dependencies And Integration Points
It depends on smbconf private APIs plus text and registry backend initializers. It is used by C and Python wrappers as a single entry point for backend selection.

## Risks And Test Signals
Risks include ambiguous strings with colons, empty sources, backend aliases, and fallback masking typos in backend names by attempting file open. Tests should cover `registry:`, `reg:PATH`, `file:PATH`, `txt:PATH`, bare file path, unknown backend with colon, NULL/empty source, and NULL output pointer.
