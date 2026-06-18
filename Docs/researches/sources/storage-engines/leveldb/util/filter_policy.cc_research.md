# sources/storage-engines/leveldb/util/filter_policy.cc

## Purpose
`filter_policy.cc` provides the out-of-line virtual destructor for `FilterPolicy`.

## Important APIs, Types, and Functions
Only `FilterPolicy::~FilterPolicy` is defined.

## Control Flow
There is no runtime control flow beyond virtual destruction.

## State, Dependencies, and Integration
The destructor definition anchors the interface declared in `leveldb/filter_policy.h`, allowing policies such as the built-in Bloom filter and test filters to be deleted through base pointers.

## Risks and Test Signals
The risk is minimal but necessary ABI/link correctness. Bloom and filter block tests delete policies through base pointers and rely on this definition.
