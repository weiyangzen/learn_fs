# sources/test-tools/fio/thread_options.h

## Purpose
`thread_options.h` is fio's central job-option schema. It defines in-memory `struct thread_options`, packed/network `struct thread_options_pack`, option-related enums and helper structs, and conversion/parser function prototypes.

## Important APIs, Types, and Functions
Enums include `fio_zone_mode`, `fio_memtype`, and `dedupe_mode`. Helper structs model split syntax: `split`, `split_prio`, `bssplit`, and `zone_split`. `struct thread_options` contains the live option set used by jobs: filenames, ioengine, direction, sizes, block sizes, verification, randomization, logs, rate limiting, cgroups, flow, zbd controls, FDP, latency, and many booleans/counters. `struct thread_options_pack` is the packed representation used for client/server or cross-endian conversion, with fixed-size string fields and trailing `patterns[]`.

Declared APIs include `convert_thread_options_to_cpu()`, `thread_options_pack_size()`, `convert_thread_options_to_net()`, `fio_test_cconv()`, `options_default_fill()`, `str_split_parse()`, `split_parse_ddir()`, and `split_parse_prio_ddir()`.

## Control Flow and State
The file is declarative, but it defines persistence and compatibility state. `set_options` tracks which options were set; `OPT_MAGIC` validates option structs; fixed maxima such as `BSSPLIT_MAX`, `ZONESPLIT_MAX`, `ERROR_STR_MAX`, and `FIO_TOP_STR_MAX` bound packed data. The packed layout is marked `__attribute__((packed))`, making field order and widths highly sensitive.

## Dependencies and Integration Points
It includes architecture, OS, option, stat, time, pattern, and error headers. It is integrated with option parsing, job creation, network protocol conversion, JSON/status reporting, zbd code, verification, logging, and ioengine-specific behavior.

## Risks and Test Signals
Risks are high: adding/reordering fields can break client/server compatibility, endian conversion, default filling, and option persistence. Pointer fields in live options require explicit packing. Test signals include cconv tests, client/server option transfer, build-time struct users, and broad fio regression tests that exercise specific option families.
