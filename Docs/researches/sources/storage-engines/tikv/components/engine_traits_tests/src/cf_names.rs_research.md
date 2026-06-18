# sources/storage-engines/tikv/components/engine_traits_tests/src/cf_names.rs

Purpose: Tests column-family name reporting through `CfNamesExt`.

Important APIs and control flow: `default_names` opens a default-only engine and expects one name equal to `CF_DEFAULT`. `cf_names` opens `ALL_CFS` and checks every expected CF is present.

State, persistence, and dependencies: Test engines create temporary DB directories with selected CFs; assertions read engine metadata.

Integration points, risks, and test signals: Provides a basic signal that constructors and `cf_names` expose CF metadata consistently. It does not require ordering for all-CF engines, only membership.
