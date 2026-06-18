# sources/user-network-fs/impacket/impacket/Dot11Crypto.py

Purpose: `Dot11Crypto.py` provides a minimal RC4 stream cipher implementation used by IEEE 802.11/WEP packet handling code.

Important APIs, types, and functions: `RC4.__init__(key)` performs the key-scheduling algorithm into `self.state`. `encrypt(data)` runs the pseudo-random generation algorithm and XORs each byte with the keystream. `decrypt(data)` delegates to `encrypt()` because RC4 is symmetric.

Control flow: Construction converts the key to a bytearray, initializes the 256-byte permutation, and swaps entries based on key bytes. Encryption resets local `i` and `j` counters to zero for each call, mutates `self.state` as it emits keystream, and returns `bytes(out)`.

State and persistence behavior: The cipher state is held in the `RC4` instance and is mutated by every encryption/decryption call. There is no external persistence. Reusing one instance for multiple independent messages continues the keystream state and can produce incorrect output if the caller expected a fresh RC4 stream per packet.

Dependencies and integration points: The module has no imports. It is used indirectly by 802.11/WEP support in the `dot11` packet classes and by decoders that decrypt protected data.

Risks: RC4/WEP is cryptographically obsolete. Empty keys cause modulo-by-zero during key scheduling. Stateful reuse is easy to misuse because `encrypt()` does not reset the permutation. There is no integrity verification here; WEP ICV checks are handled in packet-layer code.

Test signals: Tests should cover known RC4 vectors, encrypt/decrypt symmetry with fresh instances, behavior on byte-like inputs, empty-key rejection or failure behavior, and stateful reuse semantics.
