# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc2.c

LanguageLevel management operators. It implements `languagelevel` and `.setlanguagelevel`, including dictionary swapping needed when changing visible language level.

`zlanguagelevel` pushes the current interpreter level. `zsetlanguagelevel` validates the requested level and calls `set_language_level`. The setter updates global level state and swaps entries between `systemdict` and level-specific dictionaries so operators/resources appear or disappear according to the selected level.

`swap_level_dict` and `swap_entry` traverse dictionaries and exchange entries, including nested subdictionaries. The logic must preserve dictionary access and VM-space constraints while mutating system-level operator dictionaries.
