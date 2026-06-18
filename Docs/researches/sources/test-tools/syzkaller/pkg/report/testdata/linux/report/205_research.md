<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/205 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/205

## Purpose
This fixture is another CLUSTERIP proc registration warning, but with substantial unrelated TUN/VFS lock noise before and around the warning. Expected title is `WARNING: proc registration bug in clusterip_tg_check`, type `WARNING`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The parser must recognize the same proc warning as report 181 despite interleaved frames. Important visible functions include `proc_register`, `proc_create_data`, `clusterip_tg_check`, netfilter table replacement frames, and noisy frames such as `tun_build_skb.isra.50`, `build_skb`, `tun_flow_update`, `filemap_map_pages`, `tun_get_user`, and `tun_do_read`. It also uses panic-on-warn detection.

## Control Flow
The Linux reporter scans a mixed log where non-warning stack frames appear before the `WARNING: CPU ... proc_register` line. It should anchor report selection to the proc registration warning and derive the CLUSTERIP title. Panic is indicated immediately after the warning line.

## State And Persistence
The persistent state is expected metadata and a 159-line noisy report. Dynamic state includes network packets, filemap state, task ids, IP table/proc entry names, and addresses.

## Dependencies And Integration Points
It depends on warning boundary detection, proc-registration special title rules, netfilter stack parsing, and panic detection. It complements report 181 by testing noisy prelude tolerance.

## Risks
The parser could be distracted by TUN frames and title the report from `tun_get_user` or lock-acquisition helpers. It could also treat this as a duplicate of report 181 while losing the noisy-boundary regression value.

## Test Signals
Assert exact title, type, and panic flag. The report should include the `proc_register` warning and `clusterip_tg_check` frame even with surrounding TUN/VFS noise.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/205 -->
