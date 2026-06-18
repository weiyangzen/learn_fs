# sources/storage-engines/wiredtiger/test/fuzz/modify/fuzz_modify.c

Purpose: libFuzzer target for WiredTiger modify packing and application code. It turns arbitrary bytes into a base value plus one `WT_MODIFY`, packs it through internal helpers, grows a buffer, and applies the modify.

Important APIs and functions: `LLVMFuzzerTestOneInput` is the fuzzer entry point. It calls `fuzzutil_setup`, casts the session to `WT_SESSION_IMPL`, opens a `metadata:` cursor to satisfy internal helper requirements, calls `__wt_modify_pack`, `__wt_modify_max_memsize_unpacked`, `__wt_buf_set_and_grow`, and `__wt_modify_apply_item`.

Control flow and state: inputs smaller than 10 bytes return immediately. `data[0] % size` selects the initial value length; the remainder becomes modify data; `data[buf.size] % size` selects the modify offset. The cursor, scratch item, and buffer are freed before returning. The WiredTiger connection/session are reused via fuzz global state.

Dependencies and integration: includes `fuzz_util.h` and relies on WiredTiger internal symbols/macros from the test build. CMake links this target with `fuzz_util`, WiredTiger, test utilities, and libFuzzer.

Risks and test signals: this target deliberately drives internal modify paths with arbitrary offsets and sizes. It assumes `buf.size < size`, which holds because `data[0] % size` is used. The fuzzer checks for crashes, assertions, sanitizer failures, and invalid memory handling in modify pack/apply behavior rather than asserting semantic output.
