# File Research: sources/os/bsd/netbsd-src/lib/libpam/libpam/Makefile

Builds the NetBSD OpenPAM library. It sets `LIB=pam`, `SHLIB_MINOR=1`, pulls OpenPAM source/man files from `external/bsd/openpam/dist`, enables `HAVE_CONFIG_H`, and adds NetBSD's local `pam_debug_log.c`.

It installs OpenPAM/PAM public headers plus `pam_mod_misc.h`, lists extensive manual pages, and assembles `openpam_static_modules.o` by whole-archiving configured static module libraries. Static modules include common PAM modules with Kerberos/S/Key conditional additions and `pam_ssh`.
