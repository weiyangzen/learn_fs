<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/Makefile.am -->
# sources/user-network-fs/s3fs-fuse/doc/Makefile.am

Purpose: Automake file for installing the generated s3fs manpage.

Important fields: `dist_man1_MANS = man/s3fs.1` marks the section 1 manpage for distribution and installation.

Control flow and integration: `configure.ac` generates `doc/man/s3fs.1` from `doc/man/s3fs.1.in`, and automake installs/distributes it through this variable during doc subdir processing.

State and persistence: No runtime state. The generated manpage is a build artifact; the `.in` file is the maintained source.

Dependencies and risks: Depends on `configure.ac` listing `doc/Makefile` and `doc/man/s3fs.1` in `AC_CONFIG_FILES`. If the generated manpage is missing, install/dist targets fail.

Test signals: `make -C doc distcheck` or a full `make distcheck` verifies the manpage is generated and packaged.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/Makefile.am -->
