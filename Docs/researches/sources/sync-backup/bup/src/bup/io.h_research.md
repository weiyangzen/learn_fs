## sources/sync-backup/bup/src/bup/io.h

Purpose: header declaring C diagnostic helpers.

Important APIs: declares `msg()` and `die()` for use by launcher/support code.

State and risks: no state. It must stay in sync with printf attributes and signatures in `io.c`; consumers rely on `die()` not returning.
