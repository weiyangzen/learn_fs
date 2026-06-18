# File Research: sources/os/plan9/9front/sys/src/cmd/dict/simple.c

Simple UTF dictionary adapter.

Key elements:
- Handles dictionaries where each entry is one line and headword is separated from body by a tab.
- `simpleprintentry` prints headword only for `h`; otherwise replaces the tab with a space and prints until newline.
- `simplenextoff` advances to the next newline.
- `simpleprintkey` reports no key.

Dependencies:
- Used by Russian-English and English-Russian dictionaries in `utils.c`.

Research notes:
- This is the minimal adapter contract implementation.
