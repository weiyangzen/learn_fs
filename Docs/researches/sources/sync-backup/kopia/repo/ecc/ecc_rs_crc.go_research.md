# sources/sync-backup/kopia/repo/ecc/ecc_rs_crc.go

## Purpose
Implements `REED-SOLOMON-CRC32`, an error-correction transform that appends parity shards and CRC32 checksums to stored data. It can reconstruct corrupted or missing shards during decrypt/read.

## Important APIs, Types, And Functions
`ReedSolomonCrcECC` implements `encryption.Encryptor` with `Encrypt`, `Decrypt`, and a panic-only `Overhead`. Construction happens through `newReedSolomonCrcECC`, registered in `init`. Sizing helpers include `computeSizesFromOriginal`, `computeSizesFromStored`, `readLength`, `computeFinalFileSizeWithPadding`, and `sizesInfo`.

## Control Flow
Construction chooses `MaxShardSize` from overhead if absent, subtracts CRC overhead from the space budget, computes data/parity shard counts, sets small-file and block thresholds, and creates Reed-Solomon encoders. Encryption prepends original length, pads as needed, splits data into shards, computes parity, writes CRC+parity shards first, then writes CRC+data shards. Decryption reconstructs the same sizing from stored length, verifies CRCs to nil out corrupted shards, optionally deletes the first shard for tests, asks Reed-Solomon to reconstruct data shards, reads the embedded original length, and appends only original payload bytes.

## State And Persistence
The persisted byte layout is `([CRC32][parity shard])*` followed by `([CRC32][data shard])*`, potentially across blocks. Small files store padding; larger files avoid storing trailing padding and infer it on read.

## Dependencies And Integration Points
Depends on `github.com/klauspost/reedsolomon`, CRC32, binary big endian encoding, `gather`, and `repo/encryption`. It is inserted by the format provider as the outer transform after content encryption.

## Risks And Edge Cases
Correctness depends on exact symmetry between stored-length and original-length sizing. CRC32 is for corruption detection, not cryptographic authentication. `Overhead` panics because overhead is variable; callers must not use ECC wrappers where fixed overhead is required. Very small shard sizes require special `readLength` cases because the four-byte original length spans multiple shards.

## Test Signals
`ecc_rs_crc_test.go` checks fixed overhead examples, data/parity CRC corruption, reconstructable and unreconstructable numbers of changed shards, and monotonic sizing in a skipped slow test.
