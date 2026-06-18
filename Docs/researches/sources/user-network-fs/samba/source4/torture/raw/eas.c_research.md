# sources/user-network-fs/samba/source4/torture/raw/eas.c

Purpose: This file tests SMB1 extended attribute behavior for setfileinfo EA updates, bad EA name validation, maximum EA size probing, and NTTRANS create with initial EAs.

Important APIs, types, and functions: `check_ea()` wraps `torture_check_ea()`. `test_eas()` drives `RAW_SFILEINFO_EA_SET`. `test_one_eamax()` binary-searches usable EA value length for one EA name. `test_max_eas()` probes aggregate EA capacity using torture options. `test_nttrans_create()` uses `RAW_OPEN_NTTRANS_CREATE` with `struct smb_ea_list`. Entrypoints are `torture_raw_eas()` and `torture_max_eas()`.

Control flow: `test_eas()` creates `ea.txt`, adds two EAs, modifies one, sets a null EA, deletes EAs by setting zero-length values, verifies bad names reject the entire batch, and iterates byte values in a generated EA name to distinguish invalid control/reserved characters from accepted characters. `test_max_eas()` reads options `maxeasize`, `maxeanames`, `maxeastart`, and `maxeadebug`, fills a deterministic blob, then probes per-name maximums and total accepted EA bytes. `test_nttrans_create()` creates a file with three initial EAs, verifies EAs are not applied when opening an existing file, and verifies bad initial EA names fail atomically without creating the file.

State and persistence behavior: It creates files under `\\testeas` and mutates EAs. `torture_raw_eas()` does not delete the tree at the end, while `torture_max_eas()` deletes it unless `maxeadebug` is set, intentionally preserving files for inspection.

Dependencies and integration points: It depends on raw open, setfileinfo, NTTRANS create, EA list structures, `torture_check_ea()`, data blobs, torture option parsing, and server filesystem EA support.

Risks: EA support and limits vary widely by backend filesystem and server configuration. The max-size probe can be expensive with high options. Bad-name behavior must be atomic; partial EA application would indicate a server bug and can pollute later checks.

Test signals: Passing shows EA add/modify/delete semantics, null values, name validation, atomic rejection, initial-create EA handling, and reported capacity behavior are consistent with expected SMB1 EA semantics.
