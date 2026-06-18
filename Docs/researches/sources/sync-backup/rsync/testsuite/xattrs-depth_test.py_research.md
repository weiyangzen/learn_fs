# sources/sync-backup/rsync/testsuite/xattrs-depth_test.py

Purpose: companion depth test for `-X` xattr preservation, ensuring xattrs on both directories and files survive through deep parent chains.

Important APIs and flow: skips when `xattrs_supported()` is false. It builds a depth-3 tree, collects relative directories and files, then sets a distinct `depth` user xattr value on every entry from inside the source directory. It captures expected xattrs with `xattr_dump()`, runs `rsync -aX -f-x_system.* -f-x_security.* --super`, then dumps destination xattrs and diffs on mismatch.

State and persistence: fixture state is recreated, and xattr values include the relative path to catch swaps. The process changes CWD to source and destination for tool-friendly relative paths.

Dependencies and integration: exercises `xattrs.c` end-to-end, xattr filters, super/fake namespace handling, and deep path operations. Risks are filesystem/xattr namespace support and privilege-dependent system/security attrs, handled by skips and filters. Test signal is exact dump equality.
