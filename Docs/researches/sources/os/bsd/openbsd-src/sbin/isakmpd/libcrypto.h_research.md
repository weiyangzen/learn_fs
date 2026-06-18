# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/libcrypto.h

Central OpenSSL include wrapper.

It includes the OpenSSL headers used by this daemon for SSL/BIO/MD5/PEM/RSA/X509/X509 verification APIs, allowing local code to include `libcrypto.h` instead of repeating OpenSSL header sets.
