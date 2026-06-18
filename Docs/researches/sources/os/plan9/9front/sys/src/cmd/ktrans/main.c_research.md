# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/main.c

`ktrans` is a threaded keyboard input method/transliterator for English, Japanese hiragana/katakana, Korean Hangul, Chinese Wubi/Pinyin-style dictionary lookup, and Vietnamese Telex.

Major pieces:
- UTF helpers `pushutf()`, `peekstr()`, and `Str` operations manage bounded UTF-8 edit buffers.
- `openmap()` loads romanization maps into `Hmap`, including partial prefixes marked `leadstomore`.
- `opendict()` loads dictionaries mapping readings to candidate lists.
- Language switching uses control characters and `langtab`/`langcodetab`.
- `displaythread()` optionally opens a Draw window showing conversion candidates, selection highlight, scrollbar, and exit area.
- `dictthread()` tracks Japanese/Chinese candidate conversion state, okuri/joshi handling, selection cycling, and candidate replacement via emitted backspaces/output.
- `telexlkup()`, `dubeollkup()`, and `dubeolbksp()` implement Vietnamese and Korean composition behavior.
- `keythread()` is the main transliteration state machine: language switching, literal mode, dictionary forwarding, map lookup, backspace handling, and output replacement.
- `kbdtap()` reads keyboard messages, `kbdsink()` writes output messages, and `plumbproc()` receives language changes from plumbing.
- `threadmain()` parses `-l` and `-G`, opens keyboard or stdin/stdout, starts channels/threads, loads `/lib/ktrans` maps and dictionaries plus optional user dictionary overlays.

The program is Plan 9 UI/input infrastructure code built around libthread channels, `/dev/kbdtap`-style messages, Draw, mouse/keyboard controls, and plumbing.
