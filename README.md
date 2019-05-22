# automate-sfpack-sfark
Automate packing and unpacking soundfonts

Use this tool to *safely* compress a .sf2 to a .sfark. It runs sfark.exe and drives its ui, then the open-source sfarkxtc tool confirms that the input and output are 100% identical.

To batch-compress all sf2 soundfonts in a directory, run
`python src/automated_sfark_compress.py /directory/with/soundfonts`
or
`python src/automated_sfark_compress.py /directory/with/soundfonts --recurse`

To batch-decompress all sfpack files in a directory, run
`python src/automated_sfpack_decompress.py /directory/with/sfpacks`
or
`python src/automated_sfpack_decompress.py /directory/with/sfpacks --recurse`

The scripts can be imported as a module if you'd like to do something more complicated. Use [sfarkxtc](https://github.com/moltenform/sfarkxtc-windows) to convert sfark to sf2; and this tool does not yet support creating sfpack.
