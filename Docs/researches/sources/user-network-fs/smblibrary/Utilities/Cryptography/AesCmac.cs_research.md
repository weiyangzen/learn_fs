# sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCmac.cs

Purpose: `AesCmac` computes AES-CMAC authentication tags.

Important APIs/types/functions: `CalculateAesCmac(key, buffer, offset, length)` slices input and delegates; `CalculateAesCmac(key, data)` generates subkeys, pads if necessary, encrypts with AES-CBC/no padding, and returns the final block; private `AESEncrypt` and `Rol`.

Control flow: AES encrypts a zero block to get L, left-shifts to K1 and conditionally XORs Rb, repeats for K2, mutates or pads the last data block, encrypts the full message under CBC with zero IV, and copies the last 16 bytes.

State and persistence behavior: stateless, but `CalculateAesCmac(key, data)` mutates the caller's `data` array for full-block messages and after padding reassignment for partial blocks.

Dependencies and integration points: uses `ByteReader`, `ByteUtils`, and `RijndaelManaged`; relevant for SMB signing or other protocol MACs.

Risks: mutating caller-provided data is surprising and can corrupt buffers reused by callers. Legacy AES API. No key length validation beyond crypto provider exceptions. No tests visible here.

Test signals: NIST SP 800-38B vectors, empty message, full-block and partial-block messages, assertion that input data is or is not mutated, and invalid key length behavior.
