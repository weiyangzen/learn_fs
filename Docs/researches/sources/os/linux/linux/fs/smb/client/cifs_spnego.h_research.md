# File Research: sources/os/linux/linux/fs/smb/client/cifs_spnego.h

SPNEGO upcall ABI header for CIFS.

Defines `CIFS_SPNEGO_UPCALL_VERSION` as `2` and the variable-length `cifs_spnego_msg` payload returned by userspace: version, flags, session-key length, security-blob length, and concatenated data.

Exports the `cifs.spnego` key type and declares `cifs_get_spnego_key()`.
