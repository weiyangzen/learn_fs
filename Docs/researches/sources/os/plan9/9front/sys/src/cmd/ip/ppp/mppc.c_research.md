# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/mppc.c

Microsoft Point-to-Point Compression/encryption support for PPP. The compressor keeps 8 KiB history arenas and a rolling hash table, emits literal/copy codes, handles history reset/front flags, packet counts, optional RC4 encryption, and falls back to uncompressed packets when compression expands data and encryption is not required.

The decompressor validates packet counts, handles reset/front/encryption flags, updates RC4 keys on count boundaries, reconstructs compressed streams into history, returns reset requests on loss or decode failure, and extracts the original PPP protocol from the decompressed frame.

It also provides MPPE-style asymmetric key derivation and key updates using SHA-1 plus RC4, and includes diagnostic IP/TCP/UDP checksum/history validation helpers used for debugging decompression correctness.
