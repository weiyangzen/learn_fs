<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/thread.h -->
# sources/storage-engines/wiredtiger/test/fops/thread.h

Purpose: shared header for the fops test sources, declaring globals and operation entry points.

Important declarations: includes `test_util.h` and `<signal.h>`. Extern globals include `use_txn`, `WT_CONNECTION *conn`, `nops`, `uri`, `config`, and `pthread_rwlock_t single`. Function prototypes cover `fop_start()` and every object operation implemented by `fops_file.c`.

State contract: this header centralizes process-wide mutable state owned by `t.c` and consumed by worker/operation modules. `single` protects unique URI id generation, while `conn` is the shared WiredTiger connection used by all worker sessions.

Dependencies and integration: included by all fops C files. It exposes WiredTiger and pthread/test utility types needed across modules.

Risks and test signals: broad extern global state keeps the test simple but tightly couples all translation units. Any change to transaction behavior, object config, or URI selection in `t.c` immediately affects all operation functions. Missing prototypes here would hide integration errors between the worker dispatcher and operation implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/thread.h -->
