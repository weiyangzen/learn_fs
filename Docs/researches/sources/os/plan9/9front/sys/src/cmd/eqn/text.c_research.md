# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/text.c

This file converts eqn text tokens into troff strings and tracks spacing/font metadata for later box composition.

Key responsibilities:
- Defines the character-class spacing matrix used by `eqnbox` and text conversion.
- Converts UTF-8-ish input tokens rune by rune with `textc`.
- Handles quoted text, spaces, thin spaces, tabs, reserved words, letters, digits, punctuation, operators, arrows, troff escapes, and special italic `f`/`j`.
- Adds font transitions and class-based padding through `cadd`, `sadd`, `shim`, and `pad`.
- Sets box height, baseline, left/right font, and left/right class.

Important implementation notes:
- Quoted text without embedded `\f` is wrapped in the current font.
- Reserved words are looked up in `restbl`.
- `cadd` emits font changes only when needed and uses `wctomb` for runes.
- Warnings are emitted for unquoted troff commands other than simple `\(xx` forms.
