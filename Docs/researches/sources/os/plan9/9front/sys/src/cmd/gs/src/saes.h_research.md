# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.h

Declares Ghostscript’s AES stream state for this 9front tree. It includes `scommon.h`, enables `_PLAN9_SOURCE`, and includes Plan 9 `<libsec.h>`.

The state stores key bytes, key length, CBC IV, initialization flag, padding mode, and an embedded `AESstate`. It exposes key setup, padding setup, the AES stream template, and a buffer processing declaration.

Dependencies include Ghostscript stream state conventions and Plan 9 libsec. This is a 9front-specific adaptation compared with heap-context AES implementations in some Ghostscript versions.
