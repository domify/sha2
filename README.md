# sha2

SHA-256 for ris with the processor's SHA instructions: RustCrypto sha2
0.10.9's x86_64 backend, ported. On an x86_64 processor with SHA-NI it
hashes about 2 GB/s on one core, as OpenSSL does; elsewhere it uses the
software rounds.

```
require github.com/domify/sha2 v0.1.0 as sha2
```

```crystal
import sha2/sha2/sha256::{Sha256}

Sha256.hexdigest("abc") # => "ba7816bf..."

digest = Sha256.new
digest.update(part) # a Str or a String, as often as the data arrives
digest.hexfinal     # or `final`: the 32 bytes, or `hexfinal(w)` onto a
                    # Str::Builder
```

`Sha256` is a struct: a digest is a value on the stack, and hashing
allocates nothing. It is copied when passed, so `update` answers `Nil`
rather than a copy to chain on: keep a digest in a variable or a field.

The digests are FIPS 180-4's, the same as std/digest's `SHA256`.

## Speed

A 416,074-byte page, one core of a Ryzen 7 PRO 6850U, `--release`:

| | Per page |
|---|---|
| std/digest `SHA256` | 1.12 ms |
| `Sha256` (SHA-NI) | 0.21 ms |

## How it works

- `sha2/sha256.ri`: the asm block is x86.rs's `digest_blocks`, one
  instruction per intrinsic, written by `tools/gen_asm.py`. `cpuid` is
  asked once for SHA-NI, SSSE3 and SSE4.1.
- A `Str` is read as the tape allows: whole blocks eight bytes a load
  into a one-block buffer in the digest, hashed from there.
- The module is `@[Ffi]`, as the asm takes pointers; the API has none.

## Checks

```sh
./check.sh
```

`sha2/sha256_test.ri` holds both paths to std/digest's `SHA256`: every
length to 2,100 bytes, whole and in uneven pieces, and 1 MB.
