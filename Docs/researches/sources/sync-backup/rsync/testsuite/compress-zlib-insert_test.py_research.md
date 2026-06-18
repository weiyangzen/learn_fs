# sources/sync-backup/rsync/testsuite/compress-zlib-insert_test.py

Purpose: regression for issue #951 in zlib delta uploads where inserting a large matched block into deflate history could overflow or leave pending output.

Important APIs/types/functions: `make_data_file`, daemon config, `start_test_daemon`, `rsync_argv('-zI', '--compress-choice=zlib', '--no-whole-file', '--block-size=65535')`, `filecmp.cmp`, and `test_fail`.

Control flow: create an 8 MiB incompressible source, copy it into daemon module as basis, alter a few bytes in source, start writable daemon, force a compressed delta upload with a block size larger than the deflate output buffer, then require success and byte-identical module file.

State and persistence behavior: module basis file and changed source trigger many matched-token inserts into compressor history. Final module file must equal source.

Dependencies and integration points: daemon connection, zlib compressor path, delta token generation, and block-size handling.

Risks and test signals: local transfers would skip the needed compression path, so daemon transport is essential. Failure is nonzero transfer or corrupt uploaded file.
