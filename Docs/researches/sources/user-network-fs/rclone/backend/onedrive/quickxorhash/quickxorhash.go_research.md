# sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash.go

Purpose: implements Microsoft's QuickXorHash as a Go `hash.Hash`, used by the OneDrive backend for the `quickxor` rclone hash type. It is a non-cryptographic rolling XOR hash with a 20-byte output and 64-byte preferred block size.

Important APIs and types: constants `BlockSize`, `Size`, `shift`, `widthInBits`, and `dataSize` define the algorithm dimensions. `quickXorHash` stores a `data` array of `dataSize` bytes and a cumulative `size`. `New` returns a `hash.Hash`; `Sum(data []byte)` is a convenience one-shot function. Methods `Write`, `Sum`, `Reset`, `Size`, and `BlockSize` satisfy `hash.Hash`.

Control flow: `Write` XORs input bytes into a circular `data` buffer, first filling any remainder from previous writes and then processing full `dataSize` cycles. `xorBytes` uses `crypto/subtle.XORBytes`. `checkSum` walks the internal data array, applies the 11-bit rotating shift into a 21-byte scratch buffer, folds byte 20 into byte 0, and XORs the little-endian file length into the final eight bytes. `Sum` appends the first 20 bytes of `checkSum` without mutating state. `Reset` zeroes all state.

State and persistence behavior: all state is in-memory inside `quickXorHash`; no external persistence exists. The `size` counter is part of the hash result, so two inputs with equal XOR state but different lengths produce different sums.

Dependencies and integration points: depends only on the standard `hash` interface and `crypto/subtle`. The OneDrive backend registers it through `hash.RegisterHash("quickxor", "QuickXorHash", 40, quickxorhash.New)` and decodes Graph QuickXorHash values from base64 to hex for comparisons.

Risks: correctness is sensitive to circular offset handling across multiple `Write` calls and to the final bit shifting/folding. It is not cryptographic and should only be used for service-compatible integrity comparisons. The implementation assumes `subtle.XORBytes` behavior and ignores its return except to advance by the number XORed.

Test signals: the companion tests validate many base64 vectors, chunked writes at multiple block sizes, `Size`, `BlockSize`, `Reset`, `hash.Hash` conformance, and benchmark throughput.
