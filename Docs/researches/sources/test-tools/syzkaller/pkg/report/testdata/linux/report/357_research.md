<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/357 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/357

## Purpose
This fixture validates KASAN use-after-free read parsing in network ICMP error handling. The expected title is `KASAN: use-after-free Read in icmp_send`, alt `bad-access in icmp_send`, type `KASAN-USE-AFTER-FREE-READ`.

## Important APIs, Types, And Functions
The root marker is `BUG: KASAN: use-after-free in do_raw_spin_trylock`, with read size/address metadata. The meaningful stack includes `_raw_spin_trylock`, `icmp_send`, `ip_options_compile`, `ip_rcv_finish_core`, `ip_rcv`, `__netif_receive_skb`, `napi_gro_frags`, and `tun_get_user`. Network noise includes `protocol 88fb is buggy` messages.

## Control Flow
The parser must classify this as a KASAN use-after-free read, then choose `icmp_send` rather than low-level spinlock/KASAN helper frames. It should treat protocol warning lines as incidental console noise.

## State And Persistence
The fixture persists title, alt, and KASAN type. The raw log stores network receive path state, KASAN shadow/provenance sections, and syzkaller executor context.

## Dependencies And Integration Points
It depends on KASAN use-after-free subtype parsing, read/write access extraction, bad-access alt generation, networking frame selection, and report-boundary handling around interleaved protocol warnings.

## Risks
The immediate fault is in `do_raw_spin_trylock`; if frame ranking changes, the title can regress away from the network API where the bug manifests.

## Test Signals
Expected output is `KASAN: use-after-free Read in icmp_send`, alt `bad-access in icmp_send`, type `KASAN-USE-AFTER-FREE-READ`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/357 -->
