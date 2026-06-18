<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_gss.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_gss.py

Purpose: RPCSEC_GSS security flavor for pynfs, implementing context initialization, per-call credentials/verifiers, integrity/privacy wrapping, reply unwrapping, and verifier checking for GSS/Kerberos-backed RPC.

Important APIs/types/functions: `show_minor()`, `show_major()`, and `hint_string()` format GSS/Kerberos errors. `SecAuthGss` manages per-thread GSS packers/unpackers, `gss_seq_num`, `gss_handle`, and `gss_context`. `initialize()` performs the RFC 2203 context creation loop by sending NULL RPC calls with tokens. `make_cred()` emits INIT, CONTINUE_INIT, or DATA credentials. `secure_data()` and `unsecure_data()` implement `rpc_gss_svc_none`, integrity, and privacy services. `make_reply_verf()` and `check_verf()` create/verify sequence-number MICs.

Control flow/state: initialization is explicitly not thread-safe; after completion, calls increment `gss_seq_num` under a lock. Integrity wraps opaque `seq+data` plus checksum; privacy wraps encrypted `seq+data`. Server-side `handle_proc()` can accept INIT but other GSS procedures remain stubbed.

Dependencies/integration: imports `gssapi`, generated GSS constants/types/packers, and RPC constants. `rpc.py` adds GSS to supported flavors only if this module imports successfully.

Risks/test signals: several comments mark stubs or API drift risks, including server-side limited procedure handling and sequence overflow. Bugs would surface as `SecError`, GSS exceptions, verifier failures, mismatched sequence numbers, or RPC auth errors.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_gss.py -->
