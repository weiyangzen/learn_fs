# sources/object-store/rustfs/crates/heal/tests/heal_bug_fixes_test.rs

This regression suite covers targeted heal bug fixes. It verifies invalid negative endpoint indexes in `HealEvent::DiskStatusChange` return an error instead of panicking, valid indexes create erasure-set heal requests, object corruption maps to high-priority object healing, and EC decode failures map to urgent EC decode healing. It also tests set-disk-id signed formatting, resume timestamp construction, and task creation/status behavior.

The async transient-skip test uses a full `HealStorageAPI` mock with atomics to ensure an `Error::transient_skip` from `object_exists` completes the task without calling `heal_object`, preventing recreate work during quorum/lock races. Most tests are synchronous and do not touch disk.

Integration points include `heal::event`, `heal::task`, `heal::utils`, `heal::resume`, ECStore endpoint types, and `rustfs_common::heal_channel::HealOpts`. The mock-heavy tests validate control flow rather than real ECStore behavior, but they are strong signals for prior panic/race regressions.
