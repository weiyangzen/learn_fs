# sources/test-tools/fio/t/sgunmap-test.py

Purpose: destructive functional smoke test for fio's `sg` ioengine unmap/trim behavior. It checks reported iodepth, submit, and complete histograms for read, write, and trim workloads on sg character and block devices.

Important APIs and functions: `check()` validates JSON `iodepth_level`, `iodepth_submit`, and `iodepth_complete` buckets based on device type, queue depth, batch size, and rw mode. `runalltests()` executes read/write/trim for both character and block devices. `runcdevtrimtest()` targets additional character-device trim queue-depth/batch combinations.

Control flow: `main()` parses character device, block device, and fio executable. It first runs multiple high-depth character-device trim cases, then calls `runalltests()` for qd/batch pairs 1/1, 16/2, and 16/16. Each fio invocation emits JSON to stdout, which is parsed immediately and passed to `check()`.

State and persistence: workloads are destructive on supplied devices. The script writes no artifacts and prints parameter lists plus pass/failure details.

Dependencies and integration points: supports Python 2 and 3 via future imports, depends on fio JSON output, sg-capable devices, and permissions. It is a standalone manual test and not part of the umbrella manifest.

Risks and test signals: `check()` prints assertion failures but does not return failure status to callers, so the script may continue and potentially exit success after failed assertions. Bucket thresholds are tied to fio's histogram keys (`4`, exact batch, `>=64`). Success signals are printed `passed` messages and absence of assertion diagnostics.
