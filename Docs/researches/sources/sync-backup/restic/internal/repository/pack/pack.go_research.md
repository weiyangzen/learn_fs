
# sources/sync-backup/restic/internal/repository/pack/pack.go

Purpose: implements the restic pack-file writer and reader. A pack stores encrypted blob payloads followed by an encrypted header and a 4-byte header-length footer.

Important APIs include `NewPacker`, `Packer.Add`, `Packer.Finalize`, `Packer.Merge`, `Packer.Size`, `Packer.Count`, `Packer.HeaderFull`, `Packer.Blobs`, `List`, `CalculateEntrySize`, `CalculateHeaderSize`, and `Size`. Header entries encode blob type and length, with extra uncompressed length for compressed blobs. `Finalize` encrypts and appends the header, then verifies it by decoding it back with `List` before writing.

Control flow on read starts with `readHeader`, which eagerly reads the footer plus a small header window and only issues a second read for large headers. `List` decrypts the header, parses entries sequentially, and reconstructs offsets. `Size` computes pack sizes from index data.

State is persisted in the pack byte layout; errors mark a `Packer` as broken and future calls return `ErrBroken`. Risks include header length validation, compressed-entry compatibility, short writes, and max header size. Tests cover header parsing, eager reads, invalid headers, broken writers, pack creation, merge, and header self-verification.
