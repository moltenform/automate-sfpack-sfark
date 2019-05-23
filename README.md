# automate-sfpack-sfark
Automate packing and unpacking soundfonts

Use this tool to *safely* compress a .sf2 to a .sfark. It runs sfark.exe and drives its ui, then the open-source sfarkxtc tool confirms that the input and output are 100% identical. sfark and sfpack are closed source tools - I think driving the UI is the only possible way to accomplish batch conversion. Because driving a UI is never an exact science, I recommend keeping a backup copy of your input until you confirm that the conversion succeeded. 

To batch compress all sf2 soundfonts in a directory, run
`python src/automated_sfark_compress.py /directory/with/soundfonts`
or
`python src/automated_sfark_compress.py --recurse /directory/with/soundfonts`

To batch decompress all sfpack files in a directory, run
`python src/automated_sfpack_decompress.py /directory/with/sfpacks`
or
`python src/automated_sfpack_decompress.py --recurse /directory/with/sfpacks`

The scripts can be imported as a module if you'd like to do something more complicated. Use [sfarkxtc](https://github.com/moltenform/sfarkxtc-windows) to convert sfark to sf2; this tool does not yet support creating sfpack.

Supports attached information and license files, for both sfark and sfpack. Supports a `--continue_on_err` flag to automatically continue if any files can't be processed succesfully. To gracefully stop the script while it is running, create a file named `nocpy_request_stop` in the same directory as the script and wait about 30 seconds.

### Tests

Edit `automated_sfark_compress.py` to provide the path to `sfark.exe` and `sfarkxtc.exe`, then run

`python automated_sfark_compress.py --test 1`

Edit `automated_sfpack_decompress.py` to provide the path to `sfpack.exe`, then run

`python automated_sfpack_decompress.py --test 1`

