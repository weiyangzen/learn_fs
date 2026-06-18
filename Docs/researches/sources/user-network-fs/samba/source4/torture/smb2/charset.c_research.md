# sources/user-network-fs/samba/source4/torture/smb2/charset.c

Purpose: This file implements SMB2 charset torture tests that create files with specific Unicode names. It probes how the server handles composed characters, standalone diacritics, surrogate halves/pairs, and full-width Latin characters.

Important APIs and types: The central helper is `unicode_open()`, which converts an array of UTF-16 code units into a Unix string using `convert_string_talloc_handle()` and `lpcfg_iconv_handle()`, prefixes it with `BASEDIR`, then calls `smb2_create()` and closes the handle. Test cases are `test_composed()`, `test_diacritical()`, `test_surrogate()`, and `test_widea()`. The suite is registered by `torture_smb2_charset()`. It uses `struct smb2_create`, `smb2_util_setup_dir()`, `smb2_deltree()`, `smb2_util_close()`, and torture assertion helpers.

Control flow: Every test creates `chartest`, calls `unicode_open()` with one or more hard-coded UTF-16 code-unit arrays and `NTCREATEX_DISP_CREATE`, checks the expected NTSTATUS, then deletes the directory. `test_composed()` creates decomposed `a` plus combining diaeresis and precomposed `a-umlaut`. `test_diacritical()` creates one and two standalone combining-diaeresis names. `test_surrogate()` tries a high surrogate, a low surrogate, and a high+low pair. `test_widea()` creates ASCII `a`, full-width lowercase `a`, and expects full-width uppercase `A` to collide.

State and persistence behavior: Persistent filesystem state is limited to files under `chartest`; each test removes the tree in its `done` path. `unicode_open()` allocates temporary UTF-16 and converted-name buffers under the caller-provided talloc context and frees the UTF-16 parent before returning.

Dependencies and integration points: The tests depend on Samba charset conversion, configured iconv handles, SMB2 create/close semantics, and server-side Unicode normalization/casefolding behavior. They integrate as a normal one-tree SMB2 torture suite named `charset`.

Risks: The helper stores each `uint32_t` code point with `SSVAL`, so it is really writing UTF-16 code units; values outside 16 bits would be truncated if added later. `test_surrogate()` returns `true` unconditionally after cleanup instead of `ret`, which could hide a failure after an assertion path sets `ret = false`. Expectations are server/filesystem dependent because Unicode normalization, invalid surrogate acceptance, and wide-character casefolding vary across backends. The tests create names that may not be representable on all local or remote filesystems.

Test signals: Expected success is `NT_STATUS_OK` for composed, diacritical, and surrogate create attempts, and `NT_STATUS_OBJECT_NAME_COLLISION` for full-width uppercase `A` after ASCII and full-width lowercase `a` exist. Cleanup should delete `chartest` after every test. Conversion failures or unexpected create statuses identify charset mapping or filesystem normalization regressions.
