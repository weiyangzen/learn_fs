<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/misc.h -->
# sources/test-tools/filebench/misc.h

Purpose: defines Filebench logging level constants.

Important APIs/constants: `LOG_ERROR`, `LOG_ERROR1`, `LOG_INFO`, `LOG_VERBOSE`, `LOG_DEBUG_SCRIPT`, `LOG_DEBUG_IMPL`, `LOG_DEBUG_NEVER`, `LOG_FATAL`, and `LOG_DUMP` classify output routing and filtering in `filebench_log()`.

Control flow contract: levels below info route to stderr, normal info/debug route to stdout when enabled, fatal can be used before shared memory exists, and dump writes to the configured dump fd.

State/persistence: constants only; behavior depends on `filebench_shm->shm_debug_level`, dump state, and error suppression.

Dependencies/integration: included via project headers wherever logging occurs.

Risks: numeric values are part of implicit filtering semantics; adding intermediate values can change what existing debug settings emit.

Test signals: unit/smoke tests should assert each level's route/filter behavior through `filebench_log()`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/misc.h -->
