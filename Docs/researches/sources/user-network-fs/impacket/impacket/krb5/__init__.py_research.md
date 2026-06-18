# sources/user-network-fs/impacket/impacket/krb5/__init__.py

Purpose: marks `impacket.krb5` as a package and contains only licensing comments plus `pass`. It has no runtime exports, initialization side effects, or persistence behavior.

Important APIs/types/functions: none. Consumers import concrete submodules such as `asn1`, `constants`, `crypto`, `ccache`, `gssapi`, `kerberosv5`, `keytab`, `kpasswd`, `pac`, and `types`.

Control flow and state: module import executes no logic beyond `pass`; there is no state, I/O, or configuration.

Dependencies and integration: integration point is package identity for relative imports like `from impacket.krb5 import constants`.

Risks and test signals: low risk. Tests only need to ensure package imports continue to work and relative imports remain valid if packaging metadata changes.
