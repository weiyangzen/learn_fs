# sources/user-network-fs/impacket/tests/misc/test_crypto.py

Purpose: Verifies generic AES-CMAC helper functions against published-style vectors.

Important APIs, types, and functions: Uses `Generate_Subkey`, `AES_CMAC`, `AES_CMAC_PRF_128`, plus local formatting helpers `by8`, `hex8`, and `pp`.

Control flow: Tests derive CMAC subkeys and compare them to fixed hex strings, then compute CMAC outputs for multiple message lengths and PRF outputs for multiple key lengths.

State and persistence behavior: Pure in-memory cryptographic vector tests. No external state.

Dependencies and integration points: Supports Kerberos and other protocol code that depends on Impacket's crypto primitives.

Risks: Formatting helpers compare grouped hex text, so failures show exact byte-level differences. The unused `M` variable in `test_subkey` is harmless.

Test signals: Strong deterministic vectors for subkey generation, zero/partial/full-block CMAC, and AES-CMAC-PRF-128 key-length behavior.
