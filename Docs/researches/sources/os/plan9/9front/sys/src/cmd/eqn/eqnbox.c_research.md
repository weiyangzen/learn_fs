# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/eqnbox.c

This file concatenates two eqn boxes horizontally.

Key responsibilities:
- Sets `yyval` to the left box register.
- Computes combined baseline and height from both boxes.
- Chooses inter-box spacing with `class[rclass[p1]][lclass[p2]]` and `pad`.
- Handles lineup mode by aligning the left box to register `09`.
- Appends the right box string to the left box string.
- Propagates right font and right class metadata from the right box.
- Frees the right box register.

Important implementation notes:
- This is the core operation used by `eqn : eqn box`.
- The file keeps all spacing decisions dependent on left/right character classes, so text conversion metadata directly affects equation assembly.
