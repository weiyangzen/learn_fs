# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfzlib.c

Creates zlib and Flate stream filters for the interpreter. It registers `zlibEncode`, `zlibDecode`, `FlateEncode`, and `FlateDecode`.

`filter_zlib` initializes a zlib encoder state from `s_zlibE_template` defaults and optionally reads an `Effort` dictionary parameter in the range `-1..9`. `zzlibE` creates a raw zlib write filter, while `zzlibD` creates the matching read filter. `zFlateE` and `zFlateD` wrap the same zlib templates with predictor-aware helpers, connecting PNG/PDF predictor handling through `ifwpred.h` and `ifrpred.h`.

The file is narrow glue around Ghostscript’s stream filter templates; its main validation surface is the optional compression effort parameter and the generic filter open helpers.
