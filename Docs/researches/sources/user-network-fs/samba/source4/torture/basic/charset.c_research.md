# sources/user-network-fs/samba/source4/torture/basic/charset.c

## Purpose
This file implements SMB torture tests for Unicode filename handling. It creates names from explicit UTF-16 code units to check composed characters, naked diacritical marks, surrogate halves/pairs, and fullwidth ASCII equivalence behavior.

## Important APIs, Types, And Functions
The suite factory is `torture_charset`. Helper `unicode_open` converts an array of UTF-16 code units into a Unix string through the configured iconv handle, prefixes `\\chartest\\`, and performs a raw NTCreateX. Test cases are `test_composed`, `test_diacritical`, `test_surrogate`, and `test_widea`.

## Control Flow
Each test prepares `BASEDIR` with `torture_setup_dir`, then calls `unicode_open` with specific codepoint sequences. The composed test creates `a` plus combining diaeresis and precomposed `ä`. The diacritical test creates one and two naked combining marks. The surrogate test creates high surrogate, low surrogate, and a pair. The wide-a test creates ASCII `a`, fullwidth lowercase `a`, and expects fullwidth uppercase `A` to collide.

## State And Persistence
The tests create files under `\\chartest\\` on the target share. Memory for converted names is talloc-scoped. No repository state is changed.

## Dependencies And Integration Points
It depends on raw SMB open, charset conversion via `lpcfg_iconv_handle`, torture setup helpers, and the basic suite registration in `base.c`. It exercises server filename normalization/casefolding and Samba client charset conversion.

## Risks And Test Signals
Risks include platform filesystem normalization differences, iconv behavior for invalid surrogate code units, expectations around fullwidth case collisions, and cleanup being delegated to directory setup rather than each test. Passing tests signal that the server accepts edge Unicode names and applies expected equivalence/collision behavior.
