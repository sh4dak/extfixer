Python3-based utility to fix wrong extensions of your files.

## Requirements
Python 3:

https://www.python.org/

Other dependencies in txt file:

```bash
pip3 install -r requirements.txt
```

## Usage

```bash
extfix [-d %depth%] [-v] %path%
```

```-d``` or ```--depth``` flag used for recursion
```-v``` or ```--verbose``` flag used for logging
if ```%path%``` is directory, it will scan it, then fix files with wrong extension.


### Note

Feel free to contribute to csv dictionary, if it hasn't those files, you need to be fixed

It consists of mime-types and extensions
