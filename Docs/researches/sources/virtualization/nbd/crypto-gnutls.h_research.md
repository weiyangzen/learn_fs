# File Research: sources/virtualization/nbd/crypto-gnutls.h

Public TLS proxy interface.

It declares `tlssession_init()`, opaque `tlssession_t`, `tlssession_new()`, `tlssession_close()`, and `tlssession_mainloop()`.

The constructor accepts server/client mode, key/cert/CA files, hostname, GnuTLS priority string, insecure/debug flags, quit callback, error-output callback, and opaque callback data.
