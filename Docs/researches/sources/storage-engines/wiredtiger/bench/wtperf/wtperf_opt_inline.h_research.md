# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_opt_inline.h

## Purpose
`wtperf_opt_inline.h` is an X-macro option catalog for wtperf. It is included multiple times with different macro definitions to generate the `CONFIG_OPTS` struct fields, option descriptors, default initializer, and doxygen-style option documentation.

## Important APIs, Types, And Functions
The file defines `DEF_OPT_AS_BOOL`, `DEF_OPT_AS_CONFIG_STRING`, `DEF_OPT_AS_STRING`, and `DEF_OPT_AS_UINT32` under mode macros such as `OPT_DECLARE_STRUCT`, `OPT_DEFINE_DESC`, `OPT_DEFINE_DEFAULT`, and `OPT_DEFINE_DOXYGEN`. It lists options for backup, checkpoint, connection/session/table config, compression, population, table counts, indexing, logging, latency/throughput checks, random distributions, scans, tiered storage, transactions, truncate, and value sizing.

## Control Flow
There is no direct execution. The include mode determines whether each entry becomes a struct member, descriptor row, initializer value, or documentation row. `wtperf_config.c` depends on descriptor order matching the default struct layout.

## State And Persistence Behavior
This file defines default benchmark state such as `conn_config`, `table_config`, `icount`, `run_time`, `sample_rate`, `value_sz`, and `threads`. These defaults are copied into each `CONFIG_OPTS` instance and later written to `CONFIG.wtperf` only when processed through config parsing or derived option appends.

## Dependencies And Integration Points
It is tightly coupled to `config_opt.h`, `wtperf_config.c`, and every place that reads `CONFIG_OPTS` fields. `CONFIG_STRING` options append new configuration while `STRING` options replace values, so option classification is part of the public behavior.

## Risks
Adding, reordering, or retyping options can break struct initialization, usage output, or parser semantics. Defaults are intentionally tiny for fast basic runs, so tests that assume production-sized workloads must override them explicitly.

## Test Signals
Regenerate/compile all include modes, run `wtperf -?` or usage paths, parse each option type, and verify new options appear in defaults, descriptors, and config logging.
