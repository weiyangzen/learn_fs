# sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postrm

Purpose: Debian post-remove maintainer script that removes the CryFS APT repository and signing key on package purge.

Important APIs and types: Defines `get_apt_config`, `sources_list_dir`, `remove_repository`, and `remove_key`. It removes key ID `549E65B2` via `apt-key rm`.

Control flow: On `purge`, it deletes `$sources_list_dir/cryfs.list` and removes the apt key while ignoring key-removal failure. Remove/upgrade/abort cases no-op. Unknown arguments fail.

State and persistence behavior: Mutates system apt configuration by deleting CryFS source and key state only during purge, not ordinary remove or upgrade.

Dependencies and integration points: Registered with CPack Debian package control extras. Depends on apt-config and apt-key layout matching the postinst script.

Risks: Uses deprecated `apt-key`. Directory path concatenation differs from postinst (`echo $root$etc$sourceparts` vs slash-separated output), relying on apt-config values carrying separators. Only purge cleans up, so ordinary remove leaves the repository configured.

Test signals: Purging the package should remove `cryfs.list` and key ID `549E65B2`; other maintainer-script actions should exit without changes.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postrm` completely for this pass (45 lines, 870 bytes).
