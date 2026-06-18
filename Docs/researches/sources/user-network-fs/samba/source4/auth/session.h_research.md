# sources/user-network-fs/samba/source4/auth/session.h

Purpose: public interface for Samba authentication session construction, token generation, anonymous/system/admin sessions, transport serialization, and claims conversion.

Important APIs/types: declares `enum claims_data_present`, `struct claims_data`, `struct auth_claims`, `system_session()`, `auth_generate_security_token()`, `auth_generate_session_info()`, `auth_anonymous_session_info()`, transport conversion functions, `authsam_get_session_info_principal()`, `anonymous_session()`, `admin_session()`, and claims encode/decode helpers.

Control flow/integration: included by auth, service, RPC, and utility code that needs a complete `auth_session_info` or just a `security_token`. SAMDB and loadparm parameters are optional where callers do not need local privileges or local group expansion.

State/dependencies: defines in-memory structures only. `claims_data.flags` documents cached representations of encoded PAC bytes, decoded claims set, and converted security claims. It exposes `DATA_BLOB`, generated security/netlogon/auth NDR types, WERROR/NT time definitions, and forward declarations for loadparm/tevent/LDB types.

Risks/test signals: this is a cross-module contract; changing ownership or optional parameter semantics affects many Samba services. Build-time consumers and tests for session construction, PAC/claims, and system/anonymous/admin sessions validate it indirectly.
