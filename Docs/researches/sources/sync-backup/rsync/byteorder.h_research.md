# sources/sync-backup/rsync/byteorder.h

Purpose: little-endian byte load/store helpers for rsync's wire and digest formats.

Important APIs/types/functions: macros `CVAL`, `UVAL`, `IVAL`, `SIVAL`, `IVAL64`, `SIVAL64`, plus alignment-sensitive inline implementations. On x86/x86_64, unaligned little-endian access is used; otherwise byte-wise careful access is used.

Control flow: preprocessor selects `CAREFUL_ALIGNMENT`. Non-careful paths use packed/unaligned accessors annotated to avoid UBSan false positives where supported.

State and persistence: no state; affects serialization/deserialization of integers in buffers.

Dependencies/integration: included widely by rsync core and checksum/auth/ACL code through `rsync.h`.

Risks: undefined behavior from unaligned loads is intentionally managed but compiler/UBSan-sensitive. Endianness assumptions must match wire protocol.

Test signals: sanitizer workflow explicitly documents byteorder unaligned accessor suppression; protocol tests and checksum tests indirectly validate correctness.
