# sources/storage-engines/tikv/components/raftstore-v2/src/operation/pd.rs

## Purpose
Implements raftstore-v2 interactions with PD: store heartbeats, region heartbeats, pending/down peer reporting, split id allocation requests, split reporting, and peer-destroy notifications.

## Important APIs, Types, And Functions
`StoreFsmDelegate::on_pd_store_heartbeat` schedules periodic store heartbeats. `Store::store_heartbeat_pd` builds `pdpb::StoreStats`. `PeerFsmDelegate::on_pd_heartbeat` updates peer statistics and sends region heartbeats from leaders. `Peer::region_heartbeat_pd`, `collect_pending_peers`, `destroy_peer_pd`, `ask_batch_split_pd`, and `report_batch_split_pd` are the peer-facing PD APIs.

## Control Flow
Store heartbeat collection locks store metadata to count reader delegates, reads snapshot manager sending/receiving counts and traffic stats, swaps global written bytes/keys counters to zero, and schedules `pd::Task::StoreHeartbeat`. Region heartbeat runs on leaders after peer statistics refresh. It sends region metadata, leader peer, down peers, pending peers, write flow, approximate size/keys, and wait-data peers through `pd::Task::RegionHeartbeat`.

## State And Persistence Behavior
This file does not directly persist raft or tablet state. It derives report state from in-memory store metadata, snapshot manager counters, raft progress, apply truncated index, split-flow estimates, and peer stats. The global write counters are consumed through atomic `swap(0)`, making heartbeat reporting destructive for that interval.

## Dependencies And Integration Points
Depends on PD worker tasks, raft progress status, snapshot manager stats, `STORE_SNAPSHOT_TRAFFIC_GAUGE_VEC`, split-flow control, abnormal peer context, and global store stats. PD responses to split requests and heartbeats influence scheduling and membership outside this file.

## Risks And Edge Cases
Pending-peer detection treats progress matched below truncated index as pending, including matched zero, because merge safety requires all target peers to exist. If peer cache lookup fails under `dev_assert`, it panics; otherwise it logs. Scheduler failures only log errors, so missed heartbeats are retried by future ticks. Store heartbeat start time is cast to `u32`.

## Test Signals
No direct tests are present. Signals include PD task scheduling, store snapshot gauges, pending peer logs/metrics, the `schedule_check_split` failpoint after region heartbeat, and integration tests around split, merge, and PD heartbeat reporting.
