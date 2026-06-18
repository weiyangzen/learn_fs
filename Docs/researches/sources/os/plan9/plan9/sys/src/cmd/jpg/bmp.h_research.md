# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.h

## Purpose
Shared BMP structures and constants.

## Contents
Defines BMP compression constants (`BMP_RGB`, `BMP_RLE8`, `BMP_RLE4`, `BMP_BITFIELDS`), `Rgb`, `Filehdr`, and `Infohdr`.

## Usage
Included by the BMP reader to represent little-endian BMP file and info headers after parsing.
