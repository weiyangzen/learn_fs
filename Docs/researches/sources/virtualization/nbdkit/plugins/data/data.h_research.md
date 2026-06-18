# File Research: sources/virtualization/nbdkit/plugins/data/data.h

Small shared header for the data plugin.

Key contents:
- Enables `NBDKIT_DATA_HAVE_BASE64_SUPPORT` when GnuTLS and `gnutls_base64_decode2` are available.
- Declares `get_extra_param`, used by `format.c` for `$VAR` expansion from plugin command-line extras.
