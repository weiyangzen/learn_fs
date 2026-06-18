# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bonne.c

Read fully: 36 lines, 661 bytes. SHA-256 prefix: `74b0aaafa790df52`.

Implements Bonne projection. `bonne(par)` returns sinusoidal projection for near-zero standard parallel, otherwise stores the standard parallel and `r0`, returning `Xbonne`. `Xbonne()` computes radius and angular displacement, with special handling near the projection apex and poles, then maps to x/y.

Dependencies: `Xsinusoidal`, `deg2rad`.

Risk notes: the static function lacks an explicit return type in old C style. Uses static projection parameters.
