# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgtok.c

`msgtok` tokenizes RFC822-style messages into classifier features. It loads three precompiled DFAs from `/mail/lib/classify.re`: one for `"From "` message boundaries, one for keyword tokens, and one for ignored spans.

The scanner streams through a 1 KB sliding buffer, tracks header/body state, tags tokens from selected headers with prefixes like `From*`, `To*`, `Subject*`, and `Return-Path*`, emits `*From*` at message starts, and ignores tokens longer than `maxtoklen`.

For each emitted token it also generates normalized variants through `trim()`, prefixed as `stem*...`: stripping punctuation, compressing repeated trailing punctuation, and lowering uppercase/capitalized ASCII forms. Debug mode prints matched spans to stderr.
