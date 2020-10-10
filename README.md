# Virtools Shimmer

Make reusing proprietary building blocks library for Virtools a little bit easier.

## Quid est?

The goal of this project is to make it possible to use building blocks library built for older
Virtools versions in relatively newer Virtools authoring environments.

Currently this project focuses specifically on custom building blocks found in Ballance, and the
target Virtools platform is Virtools 2.5.

Targeting Virtools 3.0 or 3.5 is possible, but requires quite some extra work (needs shims for
VxMath as well).

## Quid ais?

Yes, this project actually works (as a proof of concept). Building blocks are registered correctly,
can be added to new compositions, and settings work as expected. However, at the time of writing,
few building blocks will correctly execute, and some build blocks cause errors on file load.

![Virtools with Building Blocks from Ballance](https://repository-images.githubusercontent.com/302700087/74075b00-0af0-11eb-9ef2-fdb32230dcb1)

## Quam utor?

- Run `scripts/gen.py` to generate the headers and trivial implementations of the shim.
- Patch the generated sources with the patches found in the `patches` folder.
- Build the project. You have to use the 32-bit version of MSVC (the `msvc_x86` environment if you are using Visual Studio). Don't forget to set the value for `VIRTOOLS_INCLUDE_DIR` and `VIRTOOLS_LIBS_DIR` to appropriate paths. Place the generated `cks.dll` in the root directory of your Virtools install.
- Patch the building block library DLL files with `scripts/bblibpatcher.py`. Place the patched DLL files in the `BuildingBlocks` folder in your Virtools install.
- Try it!

## Quid contribuere?

The only incomplete part that I can think of in this project right now is virtual function call mapping.
We need to annotate the type of `this` pointer of all virtual calls, and map the offsets to new
ones. Fortunately, thanks to [prior work of Gamepiaynmo](https://github.com/Gamepiaynmo/BallanceModLoader),
amount of work required for it has been drastically reduced.

If you are interested, feel free to contact me. No prior experience of reverse engineering required
(I don't have any of that, either)!

If you want to familiarize yourself with the project first, check out the following links:

 - [A guide to using shims to deal with incompatible runtime environments](https://www.ibm.com/developerworks/rational/library/shims-incompatible-runtime-environments/)
 - [CK2 method signature mapping spread sheet](https://docs.google.com/spreadsheets/d/1Kcml5-iAqOxchgSH-HIdsRZ2L0quyI2Vc5o_hQwmqPw/edit?usp=sharing)

## Quando perficiendum?

Quando parata est.
