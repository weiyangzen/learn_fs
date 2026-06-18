# sources/storage-engines/wiredtiger/test/suite/test_layered_config05.py

Purpose: tests disaggregated address-cookie version upgrade/downgrade compatibility across checkpoint pickup and continued writes.

Important APIs/types/functions: scenarios cover `disagg_address_cookie_upgrade` values `none`, `compatible`, `incompatible` and optional field true/false. Uses `debug_mode`, `restart_without_local_files`, role reconfiguration, `disagg_get_complete_checkpoint_meta`, checkpoint pickup via reconfigure, and expected `Unsupported disaggregated address cookie version` failures.

Control flow: leader writes 2,000 large values and checkpoints. It restarts with newer address-cookie debug settings and verifies all data. After step-up, it modifies 100 keys and checkpoints. It then steps down, captures checkpoint metadata, restarts with older `disagg_address_cookie_upgrade=none`, and tries to pick up metadata: compatible modes must succeed; incompatible must raise. Compatible paths verify data, step up, modify another range, checkpoint, then restart with newer settings and verify final data.

State and persistence behavior: state includes encoded address cookies in checkpoint metadata/pages and table values across version transitions. Compatibility controls whether older code can interpret newer cookies.

Dependencies/integration points: debug compatibility flags, checkpoint metadata pickup, page address cookie encoding, restart-without-local-files, and disaggregated role changes.

Risks: matrix expansion is significant. There is a subtle timestamp reuse in later commits, but the test focuses on compatibility and data reads.

Test signals: pass means compatible cookie formats round-trip across old/new nodes, incompatible formats are rejected, and compatible nodes can continue writing.
