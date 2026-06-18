# sources/sync-backup/git-lfs/script/hash-files

Purpose: prints multiple cryptographic digest lines for one or more files in a stable order.

Important APIs/classes: `DIGESTS` maps OpenSSL digest names to output labels; `Hasher` initializes digest contexts, updates all digests per chunk, and formats BSD-style hash lines.

Control flow: requires Ruby 3+, iterates `ARGV`, reads each file in 64 KiB chunks, updates all digest contexts, collects formatted output, sorts first by digest order then filename, and prints.

State/persistence behavior: read-only over input files. All digest results are accumulated in memory as output lines.

Dependencies/integration: used by `script/upload` finalization to create a signed multi-hash asset manifest.

Risks: digest availability depends on OpenSSL/Ruby build support. Very large file sets produce in-memory result arrays, though each file is streamed.

Test signals: stable output order and correct digest labels are the main observable behavior.
