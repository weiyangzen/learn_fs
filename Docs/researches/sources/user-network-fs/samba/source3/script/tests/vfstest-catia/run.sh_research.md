# sources/user-network-fs/samba/source3/script/tests/vfstest-catia/run.sh

Purpose: verifies `vfs_catia` filename character translation in both directory listing and directory creation directions.

Important functions and APIs: uses `vfstest`, subunit, `--option=vfsobjects=catia`, and a hard-coded `catia:mappings` table. `test_vfstest()` runs `vfstest.cmd` and expects the translated Windows filename to appear. `test_vfstest_dir()` runs `vfstest1.cmd` and checks the translated UNIX directory exists.

Control flow: create a temp directory, create a UNIX filename containing Windows-illegal characters, run the unix-to-windows translation test, and if it passes run the windows-to-unix mkdir translation test. Finally remove the temp directory.

State and persistence: uses a temporary directory under `$PREFIX` and removes it on normal completion. It creates files and directories with special characters, including byte values rendered in the current locale.

Dependencies and integration: registered as `samba.vfstest.catia` in `nt4_dc:local`. Depends on sibling command files and exact catia mapping behavior.

Risks and test signals: unquoted variable expansions around filenames with backslashes and special characters are fragile but controlled by the script's constants. Passing signals are seeing the translated Windows filename in output and finding exactly one translated UNIX directory.
