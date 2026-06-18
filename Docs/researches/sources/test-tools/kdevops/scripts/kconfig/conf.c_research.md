# sources/test-tools/kdevops/scripts/kconfig/conf.c

## Purpose
`conf.c` is the line-oriented Kconfig frontend. It parses Kconfig files, reads existing configuration, applies one of many configuration modes, prompts or auto-answers for new symbols, checks dependency errors, and writes `.config` plus generated autoconf outputs when appropriate.

## Important APIs, Types, And Functions
The main exported entry is `main()`. `enum input_mode` defines modes including `oldaskconfig`, `syncconfig`, `oldconfig`, `allnoconfig`, `allyesconfig`, `allmodconfig`, `alldefconfig`, `randconfig`, `defconfig`, `savedefconfig`, `listnewconfig`, `helpnewconfig`, and tristate rewrite modes. Key helpers are `set_randconfig_seed()`, `randomize_choice_values()`, `conf_set_all_new_symbols()`, `conf_rewrite_tristates()`, `conf_askvalue()`, `conf_string()`, `conf_sym()`, `conf_choice()`, recursive `conf()`, and `check_conf()`.

## Control Flow
`main()` parses long options, calls `conf_parse()` on the Kconfig file, then reads input configuration according to mode. Auto modes may load `KCONFIG_ALLCONFIG` seed files. It exits on read warnings when `KCONFIG_WERROR` is active. It applies defaults, random values, or tristate rewrites; interactive modes recursively prompt visible menu entries and repeatedly call `check_conf()` until no newly changeable symbols remain. Finally it checks dependency errors, writes a savedefconfig or `.config`, and for sync/build modes writes `auto.conf`, `autoconf.h`, and Rust cfg outputs via `conf_write_autoconf()`.

## State And Persistence
Global state includes `input_mode`, `indent`, `tty_stdio`, `sync_kconfig`, `conf_cnt`, reusable input buffer `line`, and `rootEntry`. It mutates symbol user defaults and flags in the shared Kconfig symbol table. Persistent outputs are written by `confdata.c`; this file decides when to call those writers. Environment variables such as `KCONFIG_SEED`, `KCONFIG_PROBABILITY`, `KCONFIG_ALLCONFIG`, and `KCONFIG_NOSILENTUPDATE` influence behavior.

## Dependencies And Integration Points
It depends on `internal.h`, `lkc.h`, menu traversal APIs, symbol APIs, expression/dependency checks, and configuration persistence APIs. It is linked by the Kconfig Makefile into the `conf` binary and also built as a prerequisite for menu frontends.

## Risks And Test Signals
Random configuration depends on environment parsing and can exit on invalid probabilities. `oldaskconfig` and `oldconfig` behavior differs depending on TTY detection. `syncconfig` with `KCONFIG_NOSILENTUPDATE` refuses implicit changes. Test signals include each mode, choice randomization respecting `KCONFIG_ALLCONFIG`, dependency error fixtures, stdin prompt scripts, and file outputs for syncconfig.
