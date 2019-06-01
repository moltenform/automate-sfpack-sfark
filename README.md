
This is probably the only tool available online that can:

Take a folder full of soundfonts and convert them all from `.sf2` to `.sfark` format.

and

Take a folder full of soundfonts and convert them all from `.sfpack` to `.sf2` format.

To convert soundfonts from `.sfark` to `.sf2` format, use [sfarkxtc](https://github.com/moltenform/sfarkxtc-windows).

### More information

The tool works by driving the ui of `sfark.exe` and `sfpack.exe`, sending window events as if you were typing keyboard shortcuts into the programs. It reads text out of the ui, so that it can extract attached text files and also determine when processing is complete.

If you provide a path to `sfarkxtc.exe`, the tool works even more safely -- it confirms for each file that the open-source sfarkxtc algorithm can decompress the sfark with 100% fidelity.

Supports attached information and licenses for both sfark and sfpack. If you provide the `--continue_on_err` flag, the script will keep continuing even if a file can't be processed succesfully. To gracefully stop the script while it is running, create a file named `nocpy_request_stop` in the same directory as the script and wait about 30 seconds. Because driving a UI is never an exact science, I recommend keeping a separate backup copy of your input until you confirm that the conversion succeeded. 

### Installation

* Get a copy of `sfark.exe`
* Modify `automated_sfark_compress.py` to point to the path to `sfark.exe`
* Get a copy of `sfpack.exe`
* Modify `automated_sfpack_decompress.py` to point to the path to `sfpack.exe`
* (Optional) Get a copy of `sfarkxtc.exe` from [here](https://github.com/moltenform/sfarkxtc-windows)
* (Optional) Modify `automated_sfark_compress.py` to point to the path to `sfarkxtc.exe`
* Install Python3
* Run `pip install pywinauto`

To batch compress all sf2 soundfonts in a directory, run
`python src/automated_sfark_compress.py /directory/with/soundfonts`
or
`python src/automated_sfark_compress.py --recurse /directory/with/soundfonts`

To batch decompress all sfpack files in a directory, run
`python src/automated_sfpack_decompress.py /directory/with/sfpacks`
or
`python src/automated_sfpack_decompress.py --recurse /directory/with/sfpacks`

(The first time you run `automated_sfark_compress.py`, it will suggest some changes to sfark settings, it's recommended that you follow the advice given).

### Tests

The following commands will start tests.

`python automated_sfark_compress.py --test 1`

`python automated_sfpack_decompress.py --test 1`

