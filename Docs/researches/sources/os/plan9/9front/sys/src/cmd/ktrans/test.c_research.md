# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/test.c

This is a black-box regression test for the `ktrans` binary. It forks `ktrans -l jp -G`, feeds keyboard messages through pipes, collects output messages, applies emitted backspaces to a Rune stack, and compares final text against expected Rune strings.

The test set covers Japanese kana/kanji conversion, Chinese conversion, Vietnamese Telex accents, and Korean Hangul composition. It also sets `zidian` to `/lib/ktrans/pinyin.dict` for the child process.

The harness validates observable input-method behavior rather than internal functions.
