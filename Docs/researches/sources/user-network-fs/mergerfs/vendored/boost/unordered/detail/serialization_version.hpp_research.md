# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/serialization_version.hpp

## Purpose

This header provides `serialization_version<T>`, a Boost.Unordered helper that captures the serialized version of another type `T` from a Boost.Serialization archive. It exists because `boost::serialization::load_construct_adl` asks user code to pass a version even though the archive already stores that version.

## Important APIs, types, and functions

`template<typename T> struct serialization_version` stores an `unsigned int value`. Its default constructor initializes `value` to `boost::serialization::version<serialization_version>::value`, which is specialized later to match `version<T>::value`.

The type supports assignment from `unsigned int` and implicit conversion to `unsigned int`, so callers can pass it where a version number is needed. Its private Boost.Serialization hooks implement `serialize`, `save`, and `load`; `save` does nothing, while `load` receives the archive-provided version parameter and stores it.

The specialization `boost::serialization::version<boost::unordered::detail::serialization_version<T>>` forwards `value` to `version<T>::value`, making this wrapper serialize with the same version metadata as `T`.

## Control Flow

During saving, the wrapper contributes no archive data. During loading, Boost.Serialization dispatches through `serialize`, `core::split_member`, and `load`, passing the version read from the archive. `load` copies that version into the wrapper instance for later use by unordered loading code.

## State and Persistence Behavior

The wrapper stores only the captured version number. It does not persist a separate field in the archive; it piggybacks on Boost.Serialization version metadata. The state is short-lived and local to deserialization.

## Dependencies and Integration Points

It depends on `boost/config.hpp` and `boost/core/serialization.hpp`. It integrates with Boost.Serialization through friendship with `boost::serialization::access`, `core::split_member`, and the `boost::serialization::version` specialization.

## Risks and Edge Cases

Correctness depends on the archive actually invoking serialization for the wrapper so that the version parameter is delivered. If `T` has no explicit version specialization, the wrapper reports the default version. The implicit conversion is convenient but can hide accidental use after default construction rather than after archive loading.

## Test Signals

Serialization tests should save data with multiple historical `version<T>` values and verify loading captures the stored value. Compile tests should confirm the wrapper has the same Boost.Serialization version as `T`. Regression tests should cover construction paths that call `load_construct_adl`.
