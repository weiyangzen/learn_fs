# File Research: sources/os/plan9/plan9/sys/src/cmd/page/filter.c

Contains conversion front-ends for formats that are first transformed to PostScript. `initfilt` runs an rc command, writes converted output to an ORCLOSE temp file, then calls `initps` on the generated stream.

`initdvi` spools stdin to disk because `dvips` wants a filename, then runs `dvips -Pps -r0 -q1 -f1`. `inittroff` pipes through `lp -H -dstdout`. `initmsdoc` pipes through `doc2ps`.

The function accepts an initial already-read buffer and either copies the remaining `Biobuf` or stdin into the converter, preserving `page`’s file type sniffing flow.
