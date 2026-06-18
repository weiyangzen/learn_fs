<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ntlmssp_generate_blob.c -->
# sources/user-network-fs/libsmb2/tests/ntlmssp_generate_blob.c

Purpose: Utility/test program that generates NTLMSSP negotiate/session blobs for inspection or regression comparison.

Important APIs, types, and functions: Main initializes an SMB2 context, accepts command-line/user parameters, calls NTLMSSP generation helpers, and prints binary/token output in a formatted form.

Control flow: Control is linear: parse arguments, create context, generate authentication blob, dump result, clean up, and exit on errors.

State and persistence behavior: Only transient heap/context state. No persistent files unless caller redirects output.

Dependencies and integration points: Depends on libsmb2 NTLMSSP/private authentication APIs and is useful for validating SPNEGO/NTLM integration.

Risks: As a generator, it can drift from wire expectations if no golden output comparison is enforced. It may expose sensitive test credentials if run with real passwords and logs captured.

Test signals: Compile/run coverage is available through the test build; no shell script in this subset compares exact blob bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ntlmssp_generate_blob.c -->
