# The Machine PT-BR Release Notes

## Overview

This branch contains the final PT-BR build for **The Machine** on Game Boy Color.
The public deliverable is the `IPS` patch, built from a clean original dump and
validated against the final translated ROM.

## Patch

- Patch file: `The Machine (U) [C]_PTBR.ips`
- Base ROM: `The Machine (U) [C].gbc`
- Target: a clean dump of the original game
- Verification: patch applied successfully to a clean ROM and matched the final
  translated build byte for byte

## Build Notes

- Full string table was translated and re-validated
- PT-BR accent tiles were patched into the font
- Line length and byte budget were enforced during the final pass
- The last edge cases were repaired manually so the build would stay stable in-game
- The final apply step was rerun after fixing the ROM offset mapping

## How It Was Made

1. Strings were extracted from the ROM text region.
2. The translation table was populated and cleaned up with automated passes.
3. Problematic lines were repaired until the CSV validated cleanly.
4. The final ROM was rebuilt from the clean dump.
5. The resulting ROM was compared against a patch-applied copy for verification.

## Contributing

Pull requests are welcome for:

- translation tweaks
- line wrapping fixes
- terminology consistency
- typo cleanup

Please keep the original context intact and respect the project limits:

- max 18 characters per line
- no extra line breaks
- translated bytes must fit the source budget
- preserve names, codes, and placeholders

## Usage

Apply the `IPS` patch to your own clean copy of `The Machine (U) [C].gbc`.
Tools like Floating IPS or Lunar IPS work fine.
