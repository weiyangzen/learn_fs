# sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-heimdal.c

## Purpose
This file builds a Heimdal-specific Kerberos canonicalization torture suite. It tests AS-REQ and TGS behavior for combinations of canonicalization, enterprise principals, uppercase usernames, Win2K option, UPNs, S4U2Self, implicit dollar removal, and AS-REQ service principals, then validates both client-side principal expectations and server-side PAC acceptance.

## Important APIs, Types, and Functions
Bit flags `TEST_CANONICALIZE`, `TEST_ENTERPRISE`, `TEST_UPPER_USERNAME`, `TEST_WIN2K`, `TEST_UPN`, `TEST_S4U2SELF`, `TEST_REMOVEDOLLAR`, and `TEST_AS_REQ_SPN` generate the test matrix. `struct test_data` stores naming inputs and booleans for each matrix dimension. `struct torture_krb5_context` owns the Samba krb5 context, target KDC address, current test data, and a packet counter. `struct pac_data` captures the principal name extracted during server-side GENSEC/PAC processing.

`test_generate_session_info_pac()` decodes a PAC via `kerberos_pac_blob_to_user_info_dc()` and generates session info without local database lookup while recording the principal string. `test_accept_ticket()` starts a server-side GENSEC krb5 context, accepts an AP-REQ blob, retrieves session info, and asserts the PAC principal matches expectation. `test_krb5_send_to_realm_canon_override()` forces TCP sends to the configured KDC address and increments packet counts. `torture_krb5_init_context_canon()` creates the Samba krb5 context and installs that send override. `torture_krb5_as_req_canon()` is the main test body. `torture_krb5_canon()` generates sub-suites for valid flag combinations.

## Control Flow
Each generated test resolves optional torture settings for UPN, service, hostname, removed-dollar enablement, machine-account expectation, and canonicalization-related loadparm values. It skips combinations that require missing UPN/SPN settings or intentionally unsupported flag mixes. It builds the requested principal string, canonical principal, and expected returned principal; parses them with Heimdal `krb5_parse_name_flags()`; sets principal name types for SPN cases; then performs password-based initial credential acquisition with canonicalize and Win2K options.

After AS-REQ, it validates expected errors for unknown SPNs, removed-dollar restrictions, or required-canonicalization policy. On success it checks client principal type/name, krbtgt server principal components and realm, stores credentials in a memory ccache, and then exercises several TGS paths: canonicalized krbtgt referral behavior, self-service ticket acquisition including S4U2Self, AP-REQ creation and acceptance, host/service ticket creation through `krb5_mk_req()`, explicit `KRB5_NT_SRV_INST` and `KRB5_NT_SRV_HST` requests, and exact request for the krbtgt from the initial ticket.

## State and Persistence Behavior
The test performs real Kerberos exchanges with the target KDC at port 88 and stores credentials in a memory ccache named from the test case. It does not write Samba databases, but it depends on live credentials, KDC policy, configured service principals, and optional UPN/SPN fixtures. Packet count is transient state used to assert expected network behavior.

## Dependencies and Integration Points
The file is tightly integrated with Heimdal-style krb5 APIs, Samba's `smb_krb5_context`, GENSEC server krb5 mechanism, PAC decoding, Samba command-line credentials, loadparm KDC policy options, and torture settings. It is registered as the `canon` Kerberos suite by `torture_krb5_canon()` in the krb5 torture module.

## Risks
The matrix is environment-sensitive: missing UPNs, host SPNs, machine-account SPNs, or removed-dollar enablement cause skips or expected failures. Assertions depend on Samba KDC options such as `kdc require canonicalization`, implicit-dollar matching, and whether acceptors report canonical client names. Heimdal client behavior around referrals and looping is encoded directly, so porting assumptions to MIT would be incorrect. Because it uses real credentials and a live KDC, failures can reflect environment provisioning rather than code regressions.

## Test Signals
Passing signals include expected AS-REQ success or precise Kerberos error codes, correct canonical client principal and krbtgt naming, expected packet counts for referral paths, correct service-ticket success/failure based on machine-account expectations, and successful server-side GENSEC acceptance with the expected PAC principal.
