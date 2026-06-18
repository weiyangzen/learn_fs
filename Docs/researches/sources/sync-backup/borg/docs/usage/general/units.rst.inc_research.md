# sources/sync-backup/borg/docs/usage/general/units.rst.inc

Purpose: documents Borg's quantity display conventions.

Important APIs and control flow: disk sizes use decimal SI powers (`kB` = 1000 bytes), while memory usage uses IEC binary prefixes (`KiB` = 1024 bytes).

State and persistence: no state; display-format contract for user output, logs, and docs.

Dependencies and integration points: stats output, progress displays, resource docs, benchmark output, and unit formatting controlled by common options such as `--iec`.

Risks: scripts parsing human output can misinterpret decimal versus binary units. Users may compare repository disk size and memory use using different scales.

Test signals: formatter tests for decimal and IEC units, `--iec` behavior where applicable, and stable output examples in generated docs.
