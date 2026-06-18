# sources/user-network-fs/samba/source4/auth/tests/heimdal_unwrap_des.c

Purpose: cmocka regression tests for Samba's bundled Heimdal GSSAPI DES3 unwrap path, focused on malformed token length handling and memory-safety boundaries.

Important APIs/helpers: wrappers for key/crypto/decrypt/checksum/parser/memcmp/malloc functions validate parameters and bounds. `get_input_buffer()` pads input data and records valid/invalid memory ranges. Tests call `_gsskrb5_unwrap()` with crafted RFC 1964 tokens.

Control flow: setup initializes a GSS acceptor context and dummy key/crypto objects. Each test builds a token, sometimes marks the context `GSS_C_DCE_STYLE`, registers expectations for crypto/checksum calls when valid, invokes unwrap, and asserts major status, confidentiality state, QOP, and output length/content.

State/dependencies/integration: only process-local test globals track valid buffer ranges and dummy crypto/key state. It compiles only for the Heimdal/internal GSSAPI path and includes Heimdal internal headers, testing behavior used by GENSEC Kerberos unwrap.

Risks/test signals: covers missing payloads, truncated headers, missing DES blocks, padding truncation, sealed/unsealed tokens, DCE style, and integer underflow leading to oversized malloc or out-of-range `ct_memcmp`. This file is selftest binary `test_heimdal_gensec_unwrap_des`.
