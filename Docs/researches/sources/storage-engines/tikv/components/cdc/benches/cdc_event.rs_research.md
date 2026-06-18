# sources/storage-engines/tikv/components/cdc/benches/cdc_event.rs

## Purpose
Benchmarks the optimized `CdcEvent::ResolvedTs::size` approximation against protobuf `compute_size`.

## APIs, Types, And Functions
`bench_cdc_event_size` builds `ResolvedTs` messages with region counts from 1 to 131,072 and compares `protobuf::Message::compute_size` with `CdcEvent::ResolvedTs::size`.

## Control Flow
For each region-count input, the benchmark group registers two benchmark functions: protobuf compute size and CDC's custom size method.

## State And Persistence
Only benchmark-local protobuf messages are created. No persistence.

## Dependencies And Integration Points
Uses `cdc::CdcEvent`, `kvproto::cdcpb::ResolvedTs`, protobuf sizing, and Criterion.

## Risks And Test Signals
The benchmark exists because resolved-ts messages can list many regions and size calculation is on the stream batching path. Unit tests also assert the approximation matches protobuf size for typical region IDs and TSOs.
