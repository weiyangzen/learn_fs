# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.nfsd.conf

## Purpose

`gpfs.ganesha.nfsd.conf` is the top-level split GPFS sample config. It composes main, logging, and export fragments using `%include`.

## Important APIs, Types, and Functions

It uses three scanner directives: `%include /etc/ganesha/gpfs.ganesha.main.conf`, `%include /etc/ganesha/gpfs.ganesha.log.conf`, and `%include /etc/ganesha/gpfs.ganesha.exports.conf`.

## Control Flow

The scanner processes includes in listed order, pushing each file onto the input stack. Main/global settings are loaded first, logging second, and export definitions last.

## State and Persistence Behavior

This file stores composition state only; the included fragments define runtime behavior. Include paths are absolute and assume files are installed under `/etc/ganesha`.

## Dependencies and Integration Points

It depends on the parser `%include` implementation and the split GPFS sample files being installed at the referenced paths.

## Risks and Edge Cases

Absolute include paths will fail in source-tree syntax tests unless files are staged into `/etc/ganesha` or paths are adjusted. If the exports fragment remains empty, the composed config may define no exports.

## Test Signals

Install-layout tests should validate all three includes resolve. Parser tests can use a temporary `/etc/ganesha`-like directory or rewrite paths to test include stack behavior.
