<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_argv.py -->
# sources/sync-backup/bup/test/ext/test_argv.py

Purpose: verifies argument byte preservation through the `test-argv` helper. Important APIs are `rand_bytes(n)`, `subprocess.check_output`, and WvTest `wvpasseq`. Control flow generates random byte strings of random lengths, passes them as process arguments to the helper, and checks the helper echoes exactly the expected argv encoding. State is ephemeral random input only; no repository is used. Dependencies include Python subprocess argument handling and the built `test-argv` binary/script on PATH. Risks are platform encoding differences, embedded NUL exclusion, and randomness making failures hard to reproduce without captured inputs. Test signal is exact byte-for-byte argv round trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_argv.py -->
