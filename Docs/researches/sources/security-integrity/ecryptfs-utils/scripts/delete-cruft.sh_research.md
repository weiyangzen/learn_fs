# sources/security-integrity/ecryptfs-utils/scripts/delete-cruft.sh

Purpose: removes generated/build/VCS cruft from an ecryptfs-utils working tree after validating it looks like the expected project.

Important APIs/commands: calls `scripts/validate-dir.sh`, removes `.git`, generated Makefiles, Debian old package dirs, libtool/build artifacts, reject/orig/temp files, patch directories, `nohup.out`, `cscope.out`, and `gui` directories.

Control flow/state: aborts if validation fails; otherwise performs many destructive removals in the current tree.

Dependencies/integration: used by tarball/release workflows.

Risks: broad `find -exec rm -rf` and unquoted patterns are dangerous outside the expected directory. Validation is shallow and only checks for marker files.

Test signals: directory validation and resulting clean tree.
